# Frontend Setup Instruction

## Prerequisites

Ensure you have a JavaScript runtime installed on your machine. You can choose either Node.js or Deno to manage project dependencies and run the frontend development server.

- [Node.js](https://nodejs.org/) OR [Deno](https://deno.com/)

## Install dependencies

Download and install all the necessary packages and libraries required by the frontend project. If you are using `npm`, the `--legacy-peer-deps` flag is included to automatically bypass potential version conflicts between third-party packages.

```bash
npm install --legacy-peer-deps
# Or using Deno
deno install
```

## Run

Start the local development server. This command will compile the frontend application and launch it in your web browser. It typically includes hot-reloading, meaning any changes you make to the source code will instantly update the UI without needing a manual refresh.

```bash
npm run dev
# Or using Deno
deno task dev
```
