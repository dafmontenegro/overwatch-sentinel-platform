package com.unal.api_gateway_ms;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Promise;
import io.vertx.core.http.HttpMethod;
import io.vertx.core.http.HttpClient;
import io.vertx.core.http.HttpClientOptions;
import io.vertx.core.http.HttpClientResponse;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.handler.LoggerHandler;
import io.vertx.ext.web.client.WebClient;
import io.vertx.core.http.HttpHeaders;
import io.vertx.ext.web.RoutingContext;

public class MainVerticle extends AbstractVerticle {

  private void startHttpServer(Promise<Void> startPromise) {
    Router router = Router.router(vertx);

    // Rutas de autenticación → proxy al microservicio FastAPI
    router.route("/api/auth/*").handler(ctx -> {
      String path = ctx.request().path().replaceFirst("/api", ""); // /auth/google, etc.
      proxyToAuthService(ctx, path);
    });

    // Rutas locales del Gateway (no autenticación)
    router.get("/api/users").handler(ctx -> ctx.response().end("Users route"));
    router.post("/api/session").handler(ctx -> ctx.response().end("Session route"));
    router.get("/health").handler(ctx -> ctx.response().end("OK"));
  }

  private String raspberrypiServiceUrl;
  private WebClient webClient;
  private HttpClient httpClient;
  private String authServiceUrl;
  private HttpClient client;

  @Override
  public void start(Promise<Void> startPromise) throws Exception {
    // Inicializar clientes HTTP
    startHttpServer(startPromise);
    this.webClient = WebClient.create(vertx);
    client = vertx.createHttpClient();
    this.httpClient = vertx.createHttpClient();

    Router router = Router.router(vertx);
    router.route().handler(LoggerHandler.create());

    router.get("/health").handler(ctx -> ctx.response().end("OK"));

    // Leer la URL del microservicio desde variables de entorno
    raspberrypiServiceUrl = System.getenv().getOrDefault("RASPBERRYPI_SERVICE_URL", "http://host.docker.internal:8081");

    // Leer la URL del servicio de autenticación desde variables de entorno
    authServiceUrl = System.getenv().getOrDefault("AUTH_SERVICE_URL", "http://osp-authentication-ms:8000");

    // Configuración de rutas
    configureVideoRoute(router);
    configureLogsRoute(router);
    configureEventsRoute(router);
    configurePlayRoute(router);
    configureRootRoute(router);
    configureAuthRoutes(router);

    

    // 🔁 Proxy para GitHub callback
    router.route(HttpMethod.GET, "/api/auth/github/callback").handler(ctx -> {
      proxyToAuthService(ctx, "/auth/github/callback");
    });

    // 🔁 Proxy para Google callback
    router.route(HttpMethod.GET, "/api/auth/google/callback").handler(ctx -> {
      proxyToAuthService(ctx, "/auth/google/callback");
    });

    vertx.createHttpServer()
        .requestHandler(router)
        .listen(8887, http -> {
          if (http.succeeded()) {
            System.out.println("🚀 API Gateway started on http://localhost:8887");
            startPromise.complete();
          } else {
            startPromise.fail(http.cause());
          }
        });
  }

  

  private void proxyToAuthService(RoutingContext ctx, String targetPath) {
    String query = ctx.request().query();
    String fullPath = targetPath + (query != null ? "?" + query : "");

    client.request(HttpMethod.GET, 8000, "osp-authentication-ms", fullPath)
        .onSuccess(req -> {
          req.headers().setAll(ctx.request().headers());
          req.send()
              .onSuccess(res -> {
                ctx.response().setStatusCode(res.statusCode());
                ctx.response().headers().setAll(res.headers());
                res.body().onSuccess(body -> ctx.response().end(body));
              })
              .onFailure(err -> {
                err.printStackTrace();
                ctx.fail(500, err);
              });
        })
        .onFailure(err -> {
          err.printStackTrace();
          ctx.fail(500, err);
        });
  }

  private void configureAuthRoutes(Router router) { // <-- Añade 'void'
    // Proxy para /auth/google
    router.get("/auth/google").handler(ctx -> {
      webClient.getAbs(authServiceUrl + "/auth/google")
          .send(ar -> {
            if (ar.succeeded()) {
              ctx.response()
                  .setStatusCode(ar.result().statusCode())
                  .headers().addAll(ar.result().headers());
              ctx.response().end(ar.result().body());
            } else {
              ctx.fail(ar.cause());
            }
          });
    });

    // Proxy para /auth/github
    router.get("/auth/github").handler(ctx -> {
      webClient.getAbs(authServiceUrl + "/auth/github")
          .send(ar -> {
            if (ar.succeeded()) {
              ctx.response()
                  .setStatusCode(ar.result().statusCode())
                  .headers().addAll(ar.result().headers());
              ctx.response().end(ar.result().body());
            } else {
              ctx.fail(ar.cause());
            }
          });
    });
    // Proxy para /protected
    router.get("/protected").handler(ctx -> {
      webClient.getAbs(authServiceUrl + "/protected")
          .putHeader("Authorization", ctx.request().getHeader("Authorization"))
          .send(ar -> {
            if (ar.succeeded()) {
              ctx.response()
                  .setStatusCode(ar.result().statusCode())
                  .headers().addAll(ar.result().headers());
              ctx.response().end(ar.result().body());
            } else {
              ctx.fail(ar.cause());
            }
          });
    });
  }

  private void configureVideoRoute(Router router) {
    router.get("/video").handler(ctx -> {
      Promise<Void> delayPromise = Promise.promise();
      // String videoServiceUrl = raspberrypiServiceUrl + "/stream"; // Asegúrate de
      // incluir
      // el endpoint correcto

      // Espera inicial de 5 segundos
      vertx.setTimer(5000, timerId -> delayPromise.complete());

      delayPromise.future().onComplete(ar -> {
        // Usar HttpClient en lugar de WebClient para streaming
        HttpClient client = vertx.createHttpClient(new HttpClientOptions()
            .setConnectTimeout(5000)
            .setIdleTimeout(0)); // Desactiva timeout para streams largos

        client.request(HttpMethod.GET, 8081, "host.docker.internal", "/stream")
            .onSuccess(request -> {
              request.putHeader(HttpHeaders.ACCEPT.toString(), "multipart/x-mixed-replace;boundary=frame")
                  .send()
                  .onSuccess(response -> {
                    // Configurar headers de respuesta
                    ctx.response()
                        .setChunked(true)
                        .putHeader(HttpHeaders.CONTENT_TYPE.toString(),
                            response.getHeader(HttpHeaders.CONTENT_TYPE.toString()))
                        .putHeader(HttpHeaders.CACHE_CONTROL.toString(), "no-cache")
                        .putHeader(HttpHeaders.CONNECTION.toString(), "close");

                    // Pipe directo del stream
                    response.pipeTo(ctx.response()).onComplete(pipeAr -> {
                      if (pipeAr.failed() && !ctx.response().ended()) {
                        ctx.fail(500, pipeAr.cause());
                      }
                      client.close(); // Cerrar cliente cuando termine
                    });
                  })
                  .onFailure(err -> {
                    ctx.response()
                        .setStatusCode(502)
                        .end("Error al obtener stream: " + err.getMessage());
                    client.close();
                  });
            })
            .onFailure(err -> {
              ctx.response()
                  .setStatusCode(503)
                  .end("Servicio de video no disponible");
              client.close();
            });
      });
    });
  }

  private void configureLogsRoute(Router router) {
    router.get("/logs").handler(ctx -> {
      this.webClient.getAbs(raspberrypiServiceUrl + "/logs")
          .send(ar -> {
            if (ar.succeeded()) {
              ctx.response()
                  .putHeader(HttpHeaders.CONTENT_TYPE, "text/plain")
                  .end(ar.result().body());
            } else {
              ctx.fail(ar.cause());
            }
          });
    });
  }

  private void configureEventsRoute(Router router) {
    router.get("/events").handler(ctx -> {
      this.webClient.getAbs(raspberrypiServiceUrl + "/events")
          .send(ar -> {
            if (ar.succeeded()) {
              ctx.response()
                  .putHeader(HttpHeaders.CONTENT_TYPE, "text/html")
                  .end(ar.result().body());
            } else {
              ctx.fail(ar.cause());
            }
          });
    });
  }

  private void configurePlayRoute(Router router) {
    router.get("/play/*").handler(ctx -> {
      String path = ctx.request().uri().replace("/play", "");
      this.webClient.getAbs(raspberrypiServiceUrl + "/play" + path)
          .send(ar -> {
            if (ar.succeeded()) {
              ctx.response()
                  .putHeader(HttpHeaders.CONTENT_TYPE, "video/x-msvideo")
                  .end(ar.result().body());
            } else {
              ctx.fail(ar.cause());
            }
          });
    });
  }

  private void configureRootRoute(Router router) {
    router.get("/").handler(ctx -> {
      ctx.response()
          .putHeader("content-type", "text/plain")
          .end("API Gateway funcionando");
    });
  }

  @Override
  public void stop() {
    if (this.webClient != null) {
      this.webClient.close();
    }
    if (this.httpClient != null) {
      this.httpClient.close();
    }
  }
}