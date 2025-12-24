# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Bingo Game Manager application built with React and TypeScript. The application manages bingo games and is built using Create React App with Chakra UI as the component library.

This app will be ran by the host of a bingo game on their mobile phone.
This game follows the British version of Bingo.

The features of the app are the following:
- The user has the ability to type in any number between 1 and 90 to record it as having been chosen.
- There is a history of which numbers have come out. The user can choose either this view or another view which shows a grid of all possible numbers with the lucky ones so far highlighted.
- The user can scan a QR code for a given ticket. The format of the QR code is described below. Scanning a QR code pops up a view of the ticket that was scanned with the numbers that have come up highlighted. Furthermore, fully-complete rows are highlighted in a different color.

QR Code format:
Each ticket has a V4 QR code on the back with M error correction and the following in binary data.
The first two bytes is the unique identifier of this ticket (little endian). The next 27 bytes are the content of each square in the
ticket from left to right, top to bottom. 0 denotes a square which has nothing in it (i.e. the player gets it "for free").

Bingo card generator:
There should also be a subdirectory containing a python script which can be used to generate tickets, in sequential order.
It produces a PDF of A4 paper such that there will be three tickets on each page. The next page is the reverse of the previous one
with the QR codes appropriately positioned such that they will fall in the correct place. It produces a CSV in which the first column is the id
and the other columns are the contents of each of the Bingo card similar to how the QR code is laid out. Remember that this is BRITISH bingo.


## Tech Stack

- **React 19** with TypeScript
- **Chakra UI** - UI component library (@chakra-ui/react)
- **Emotion** - CSS-in-JS styling (@emotion/react, @emotion/styled)
- **Framer Motion** - Animation library (required by Chakra UI)
- **Create React App** - Build tooling and development server
- **Jest & React Testing Library** - Testing framework

## Development Commands

### Start Development Server
```bash
npm start
```
Runs the app in development mode at http://localhost:3000 with hot reloading.

### Run Tests
```bash
npm test
```
Launches Jest in interactive watch mode.

To run tests in CI mode:
```bash
CI=true npm test
```

To run a specific test file:
```bash
npm test -- App.test.tsx
```

### Build for Production
```bash
npm run build
```
Creates an optimized production build in the `build/` folder.

## Architecture

### UI Components

All UI components should use **Chakra UI** components. Chakra UI is already configured in `src/index.tsx` with the `ChakraProvider` wrapper.

Import Chakra UI components like this:
```tsx
import { Box, Container, Heading, Button, Text } from '@chakra-ui/react';
```

Chakra UI uses a prop-based styling system (e.g., `py={8}`, `mb={4}`, `textAlign="center"`).

### Application Entry Points

- `src/index.tsx` - Application root, wraps App with ChakraProvider and React.StrictMode
- `src/App.tsx` - Main application component
- `public/index.html` - HTML template

### Testing

No testing shall be performed. Ignore all test files in this project.
