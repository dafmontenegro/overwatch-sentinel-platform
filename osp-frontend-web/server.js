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
app.use(
  helmet({
    contentSecurityPolicy: {
      useDefaults: true,
      directives: {
        defaultSrc:   ["'self'"],
        scriptSrc:    [
          "'self'",
          "'unsafe-inline'", // Vite HMR/dev
          "'unsafe-eval'",
        ],
        styleSrc:     ["'self'", "'unsafe-inline'"],
        connectSrc:   [
          "'self'",
          // allow websocket in dev:
          ...(!isProduction ? ["ws://localhost:*", "wss://localhost:*"] : []),
        ],
        imgSrc:       ["'self'", "data:", "blob:"],
        fontSrc:      ["'self'", "data:"],
        workerSrc:    ["'self'", "blob:"],
        objectSrc:    ["'none'"],
        baseUri:      ["'self'"],
        formAction:   ["'self'"],
        frameAncestors: ["'none'"],

        // ← Only include this in production, and with an empty array
        ...(isProduction && { upgradeInsecureRequests: [] })
      },
      reportOnly: !isProduction
    },

    // rest of your Helmet config…
    crossOriginEmbedderPolicy: false,
    hsts: {
      maxAge: isProduction ? 31536000 : 0,
      includeSubDomains: isProduction,
      preload: isProduction
    },
    noSniff: true,
    xssFilter: true,
    referrerPolicy: { policy: ['same-origin'] }
  })
)

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