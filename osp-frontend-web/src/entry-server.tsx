import { StrictMode } from 'react'
import { renderToString } from 'react-dom/server'
import { StaticRouter } from 'react-router-dom/server'
import App from './App'
import './index.css'

export function render(_url: string) {
  const html = renderToString(
    <StrictMode>
      <StaticRouter location={_url}>
        <App />
      </StaticRouter>
    </StrictMode>,
  )
  return { html }
}
