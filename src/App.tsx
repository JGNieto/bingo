import React from 'react';
import { Box, Container, Heading, Text } from '@chakra-ui/react';
import './App.css';

function App() {
  return (
    <Container maxW="container.xl" py={8}>
      <Box textAlign="center">
        <Heading as="h1" size="2xl" mb={4}>
          Bingo Game Manager
        </Heading>
        <Text fontSize="xl" color="gray.600">
          Welcome to the Bingo Game Manager
        </Text>
      </Box>
    </Container>
  );
}

export default App;
