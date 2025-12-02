# vue-project

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd) 
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Backend Configuration

The frontend connects to the backend API using configurable URLs. You can customize the backend connection in different environments:

- **Development**: Edit `.env.development` to set `VITE_BACKEND_URL`
- **Production**: Edit `.env.production` to set `VITE_BACKEND_URL`, or leave it unset to use the same origin as the frontend

Example `.env.development`:
```env
VITE_BACKEND_URL=http://localhost:5000
```

Example `.env.production`:
```env
VITE_BACKEND_URL=https://your-api-domain.com
```

If no backend URL is configured in production, the frontend will automatically use the same origin as the current page (recommended for most deployments).

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```
