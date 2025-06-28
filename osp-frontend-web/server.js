import fs from 'node:fs/promises'
import express from 'express'
import helmet from 'helmet'

// Constants
const isProduction = process.env.NODE_ENV === 'production'
const port = process.env.PORT || 5173
const base = process.env.BASE || '/'

// Cached production assets
const templateHtml = isProduction
  ? await fs.readFile('./dist/client/index.html', 'utf-8')
  : ''

// Create http server
const app = express()

// Configure Helmet with CSP
app.use(helmet({
  contentSecurityPolicy: {
    useDefaults: true,
    directives: {
      "script-src": [
        "'self'",
        "'unsafe-inline'", // Necesario para Vite en desarrollo
        "'unsafe-eval'", // Necesario para Vite HMR en desarrollo
        ...(isProduction ? [] : ["'unsafe-inline'", "'unsafe-eval'"]),
      ],
      "style-src": [
        "'self'",
        "'unsafe-inline'", // Necesario para estilos inline y CSS-in-JS
        // "https://fonts.googleapis.com"
      ],
      "connect-src": [
        "'self'",
        ...(isProduction ? [] : ["ws://localhost:*", "wss://localhost:*"]),
        // "https://api.example.com"
      ],
      "img-src": [
        "'self'",
        "data:", // Para imágenes base64
        "blob:", // Para imágenes blob
        // "https://images.unsplash.com"
      ],

      "font-src": [
        "'self'",
        "data:", // Para fuentes base64
        // "https://fonts.gstatic.com" // Si usas Google Fonts
      ],
      "worker-src": [
        "'self'",
        "blob:"
      ],
      "object-src": ["'none'"],
      "base-uri": ["'self'"],
      "form-action": ["'self'"],
      "frame-ancestors": ["'none'"],
      "upgrade-insecure-requests": isProduction ? [] : undefined
    },
    reportOnly: !isProduction,
  },
  
  // Configuraciones adicionales de seguridad
  crossOriginEmbedderPolicy: false,
  hsts: {
    maxAge: isProduction ? 31536000 : 0, // 1 año en producción, deshabilitado en desarrollo
    includeSubDomains: isProduction,
    preload: isProduction
  },
  
  // Previene ataques MIME sniffing
  noSniff: true,
  // Previene ataques XSS
  xssFilter: true,
  // Controla el header Referrer
  referrerPolicy: {
    policy: ["same-origin"]
  }
}))

// Add Vite or respective production middlewares
/** @type {import('vite').ViteDevServer | undefined} */
let vite
if (!isProduction) {
  const { createServer } = await import('vite')
  vite = await createServer({
    server: { middlewareMode: true },
    appType: 'custom',
    base,
  })
  app.use(vite.middlewares)
} else {
  const compression = (await import('compression')).default
  const sirv = (await import('sirv')).default
  app.use(compression())
  app.use(base, sirv('./dist/client', { extensions: [] }))
}

// Serve HTML
app.use('*all', async (req, res) => {
  try {
    const url = req.originalUrl.replace(base, '')

    /** @type {string} */
    let template
    /** @type {import('./src/entry-server.ts').render} */
    let render
    if (!isProduction) {
      // Always read fresh template in development
      template = await fs.readFile('./index.html', 'utf-8')
      template = await vite.transformIndexHtml(url, template)
      render = (await vite.ssrLoadModule('/src/entry-server.tsx')).render
    } else {
      template = templateHtml
      render = (await import('./dist/server/entry-server.js')).render
    }

    const rendered = await render(url)

    const html = template
      .replace(`<!--app-head-->`, rendered.head ?? '')
      .replace(`<!--app-html-->`, rendered.html ?? '')

    res.status(200).set({ 'Content-Type': 'text/html' }).send(html)
  } catch (e) {
    vite?.ssrFixStacktrace(e)
    console.log(e.stack)
    res.status(500).end(e.stack)
  }
})

// Start http server
app.listen(port, () => {
  console.log(`Server started at http://localhost:${port}`)
})