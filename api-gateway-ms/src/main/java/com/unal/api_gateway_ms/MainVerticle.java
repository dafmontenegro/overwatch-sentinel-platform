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

public class MainVerticle extends AbstractVerticle {

  private String raspberrypiServiceUrl;
  private WebClient webClient;
  private HttpClient httpClient;
  private String authServiceUrl;

  @Override
  public void start(Promise<Void> startPromise) throws Exception {
    // Inicializar clientes HTTP
    this.webClient = WebClient.create(vertx);
    this.httpClient = vertx.createHttpClient();

    Router router = Router.router(vertx);
    router.route().handler(LoggerHandler.create());

    // Leer la URL del microservicio desde variables de entorno
    raspberrypiServiceUrl = System.getenv().getOrDefault("RASPBERRYPI_SERVICE_URL", "http://osp-processing-ms:8080");

    // Leer la URL del servicio de autenticación desde variables de entorno
    authServiceUrl = System.getenv().getOrDefault("AUTH_SERVICE_URL", "http://osp-authentication-ms:8000");

    // Configuración de rutas
    configureVideoRoute(router);
    configureLogsRoute(router);
    configureEventsRoute(router);
    configurePlayRoute(router);
    configureRootRoute(router);
    configureAuthRoutes(router);

    // Iniciar servidor HTTP
    startHttpServer(router, startPromise);
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
      String videoServiceUrl = raspberrypiServiceUrl + "/stream"; // Asegúrate de incluir
      // el endpoint correcto

      // Espera inicial de 5 segundos
      vertx.setTimer(5000, timerId -> delayPromise.complete());

      delayPromise.future().onComplete(ar -> {
        // Usar HttpClient en lugar de WebClient para streaming
        HttpClient client = vertx.createHttpClient(new HttpClientOptions()
            .setConnectTimeout(5000)
            .setIdleTimeout(0)); // Desactiva timeout para streams largos

        client.request(HttpMethod.GET, 8080, "osp-raspberrypi-ms", "/")
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

  private void startHttpServer(Router router, Promise<Void> startPromise) {
    vertx.createHttpServer()
        .requestHandler(router)
        .listen(8887, http -> {
          if (http.succeeded()) {
            startPromise.complete();
            System.out.println("HTTP server started on port 8887");
          } else {
            startPromise.fail(http.cause());
          }
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