import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Tabs,
  Stack,
  Button,
  Input,
  Text,
  Grid,
  GridItem,
} from '@chakra-ui/react';
import {
  DialogBackdrop,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogHeader,
  DialogRoot,
} from './components/ui/dialog';
import { Toaster, toaster } from './components/ui/toaster';
import QRScanner from './components/QRScanner';
import TicketDisplay from './components/TicketDisplay';
import './App.css';

export interface TicketData {
  id: number;
  numbers: number[];
}

const SESSION_STORAGE_KEY = 'bingo-called-numbers-v2';

// Numbers that are excluded from this game (will never be called)
const MISSING_NUMBERS = [20, 72];

function App() {
  // Initialize from session storage
  const [calledNumbersArray, setCalledNumbersArray] = useState<number[]>(() => {
    try {
      const stored = sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (!stored) return [];

      const parsed = JSON.parse(stored);
      // Validate that it's an array
      if (Array.isArray(parsed)) {
        return parsed;
      } else {
        console.warn('Invalid session storage data, clearing');
        sessionStorage.removeItem(SESSION_STORAGE_KEY);
        return [];
      }
    } catch (error) {
      console.error('Error loading from session storage:', error);
      sessionStorage.removeItem(SESSION_STORAGE_KEY);
      return [];
    }
  });

  const calledNumbers = new Set(calledNumbersArray);
  const [inputValue, setInputValue] = useState('');
  const [scannedTicket, setScannedTicket] = useState<TicketData | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('input');
  const inputRef = React.useRef<HTMLInputElement>(null);

  // Save to session storage whenever called numbers change
  useEffect(() => {
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(calledNumbersArray));
    } catch (error) {
      console.error('Error saving to session storage:', error);
    }
  }, [calledNumbersArray]);

  // Auto-focus input when on input tab
  useEffect(() => {
    if (activeTab === 'input') {
      // Small delay to ensure the DOM is ready
      setTimeout(() => {
        const input = inputRef.current;
        if (input) {
          input.focus();
          // For mobile Safari, we need to trigger click to show keyboard
          input.click();
        }
      }, 100);
    }
  }, [activeTab]);

  const handleAddNumber = () => {
    const num = parseInt(inputValue);
    if (isNaN(num) || num < 1 || num > 90) {
      toaster.create({
        title: 'Número inválido',
        description: 'Introduce un número entre 1 y 90',
        type: 'error',
        duration: 2000,
      });
      return;
    }

    if (MISSING_NUMBERS.includes(num)) {
      toaster.create({
        title: 'Número excluido',
        description: `El número ${num} está excluido de este juego`,
        type: 'error',
        duration: 2000,
      });
      return;
    }

    if (calledNumbers.has(num)) {
      toaster.create({
        title: 'Ya cantado',
        description: `El número ${num} ya ha sido cantado`,
        type: 'warning',
        duration: 2000,
      });
      return;
    }

    setCalledNumbersArray([...calledNumbersArray, num]);
    setInputValue('');
    toaster.create({
      title: 'Número cantado',
      description: `El número ${num} ha sido cantado`,
      type: 'success',
      duration: 1000,
    });
  };

  const handleCallButtonClick = (e: React.MouseEvent | React.TouchEvent) => {
    // Prevent the button from stealing focus from the input
    e.preventDefault();
    e.stopPropagation();
    handleAddNumber();
    // Keep focus on input to maintain keyboard
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  const handleCallButtonTouch = (e: React.TouchEvent) => {
    e.preventDefault();
    e.stopPropagation();
    handleAddNumber();
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  const handleUndo = () => {
    if (calledNumbersArray.length === 0) return;

    const lastNumber = calledNumbersArray[calledNumbersArray.length - 1];
    setCalledNumbersArray(calledNumbersArray.slice(0, -1));
    toaster.create({
      title: 'Número eliminado',
      description: `El número ${lastNumber} ha sido eliminado`,
      type: 'info',
      duration: 1500,
    });
  };

  const handleUndoButtonClick = (e: React.MouseEvent | React.TouchEvent) => {
    // Prevent the button from stealing focus from the input
    e.preventDefault();
    e.stopPropagation();
    handleUndo();
    // Keep focus on input to maintain keyboard
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  const handleUndoButtonTouch = (e: React.TouchEvent) => {
    e.preventDefault();
    e.stopPropagation();
    handleUndo();
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  const handleQRScan = (data: TicketData) => {
    setScannedTicket(data);
    setIsDialogOpen(true);
  };

  // Display numbers in reverse order (most recent first)
  const sortedCalledNumbers = [...calledNumbersArray].reverse();

  return (
    <Container maxW="container.md" py={4}>
      <Stack gap={4} align="stretch">
        <Box textAlign="center">
          <Heading as="h1" size="xl" mb={2}>
            Gestor de Bingo
          </Heading>
          <Text fontSize="md" color="gray.600">
            Bingo (1-90)
          </Text>
        </Box>

        <Tabs.Root
          value={activeTab}
          onValueChange={(e:any) => setActiveTab(e.value)}
          fitted
          variant="enclosed"
        >
          <Tabs.List>
            <Tabs.Trigger value="input">Entrada</Tabs.Trigger>
            <Tabs.Trigger value="grid">Cuadrícula</Tabs.Trigger>
            <Tabs.Trigger value="scan">Escanear Cartón</Tabs.Trigger>
          </Tabs.List>

          {/* Input and History Tab */}
          <Tabs.Content value="input">
              <Stack gap={4} align="stretch">
                <Box>
                  <Text fontWeight="bold" mb={2}>Cantar un Número</Text>
                  <Stack direction="row" gap={2}>
                    <Input
                      ref={inputRef}
                      type="number"
                      inputMode="numeric"
                      pattern="[0-9]*"
                      placeholder="Introduce número (1-90)"
                      value={inputValue}
                      onChange={(e:any) => setInputValue(e.target.value)}
                      onKeyPress={(e:any) => {
                        if (e.key === 'Enter') {
                          handleAddNumber();
                        }
                      }}
                      min={1}
                      max={90}
                      flex={1}
                      fontSize="16px"
                    />
                    <Button colorScheme="blue" onTouchStart={handleCallButtonTouch} onMouseDown={handleCallButtonClick}>
                      Cantar
                    </Button>
                    <Button
                      colorScheme="orange"
                      onTouchStart={handleUndoButtonTouch}
                      onMouseDown={handleUndoButtonClick}
                      disabled={calledNumbersArray.length === 0}
                    >
                      Deshacer
                    </Button>
                  </Stack>
                </Box>

                <Box>
                  <Stack direction="row" justify="space-between" mb={2}>
                    <Text fontWeight="bold">
                      Números Cantados ({calledNumbersArray.length}/{90 - MISSING_NUMBERS.length})
                    </Text>
                    {calledNumbersArray.length > 0 && (
                      <Button
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => {
                          if (window.confirm('¿Estás seguro de que quieres reiniciar todos los números cantados?')) {
                            setCalledNumbersArray([]);
                            sessionStorage.removeItem(SESSION_STORAGE_KEY);
                            toaster.create({
                              title: 'Reinicio completo',
                              description: 'Todos los números cantados han sido borrados',
                              type: 'info',
                              duration: 2000,
                            });
                          }
                        }}
                      >
                        Reiniciar
                      </Button>
                    )}
                  </Stack>

                  {calledNumbersArray.length === 0 ? (
                    <Box
                      p={8}
                      textAlign="center"
                      bg="gray.50"
                      borderRadius="md"
                      border="1px solid"
                      borderColor="gray.200"
                    >
                      <Text color="gray.500">Aún no se han cantado números</Text>
                    </Box>
                  ) : (
                    <Box
                      maxH="400px"
                      overflowY="auto"
                      p={4}
                      bg="gray.50"
                      borderRadius="md"
                      border="1px solid"
                      borderColor="gray.200"
                    >
                      <Grid templateColumns="repeat(5, 1fr)" gap={2}>
                        {sortedCalledNumbers.map((num) => (
                          <GridItem key={num}>
                            <Box
                              p={3}
                              bg="blue.500"
                              color="white"
                              textAlign="center"
                              borderRadius="md"
                              fontWeight="bold"
                              fontSize="lg"
                            >
                              {num}
                            </Box>
                          </GridItem>
                        ))}
                      </Grid>
                    </Box>
                  )}
                </Box>
              </Stack>
          </Tabs.Content>

          {/* Grid View Tab */}
          <Tabs.Content value="grid">
              <Stack gap={3} align="stretch">
                <Text fontWeight="bold" textAlign="center">
                  Todos los Números (1-90)
                </Text>
                <Grid templateColumns="repeat(9, 1fr)" gap={1}>
                  {Array.from({ length: 90 }, (_, i) => i + 1).map((num) => {
                    const isCalled = calledNumbers.has(num);
                    const isMissing = MISSING_NUMBERS.includes(num);
                    return (
                      <GridItem key={num}>
                        <Box
                          p={2}
                          bg={
                            isCalled
                              ? 'green.500'
                              : isMissing
                              ? 'red.400'
                              : 'gray.200'
                          }
                          color={
                            isCalled
                              ? 'white'
                              : isMissing
                              ? 'white'
                              : 'gray.700'
                          }
                          textAlign="center"
                          borderRadius="md"
                          fontWeight={isCalled || isMissing ? 'bold' : 'normal'}
                          fontSize="sm"
                        >
                          {num}
                        </Box>
                      </GridItem>
                    );
                  })}
                </Grid>

                {/* Legend */}
                <Box
                  p={3}
                  bg="gray.50"
                  borderRadius="md"
                  border="1px solid"
                  borderColor="gray.200"
                >
                  <Text fontSize="sm" fontWeight="bold" mb={2}>
                    Leyenda:
                  </Text>
                  <Grid templateColumns="repeat(1, 1fr)" gap={2}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Box w="20px" h="20px" bg="green.500" borderRadius="sm" />
                      <Text fontSize="sm">Números cantados</Text>
                    </Box>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Box w="20px" h="20px" bg="gray.200" borderRadius="sm" />
                      <Text fontSize="sm">Aún no cantados</Text>
                    </Box>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Box w="20px" h="20px" bg="red.400" borderRadius="sm" />
                      <Text fontSize="sm">Excluidos del juego (nunca se cantarán)</Text>
                    </Box>
                  </Grid>
                </Box>

                {/* Missing Numbers List */}
                {MISSING_NUMBERS.length > 0 && (
                  <Box
                    p={4}
                    bg="red.50"
                    borderRadius="md"
                    border="1px solid"
                    borderColor="red.200"
                  >
                    <Text fontWeight="bold" mb={2} color="red.700">
                      Números Excluidos ({MISSING_NUMBERS.length})
                    </Text>
                    <Text fontSize="sm" color="red.700">
                      Estos números están excluidos de este juego: {MISSING_NUMBERS.join(', ')}
                    </Text>
                  </Box>
                )}
              </Stack>
          </Tabs.Content>

          {/* Scan Ticket Tab */}
          <Tabs.Content value="scan">
            <QRScanner onScan={handleQRScan} />
          </Tabs.Content>
        </Tabs.Root>
      </Stack>

      {/* Ticket Display Dialog */}
      <DialogRoot open={isDialogOpen} onOpenChange={(e: { open: boolean }) => setIsDialogOpen(e.open)} size={{ base: 'full', sm: 'xl' }}>
        <DialogBackdrop />
        <DialogContent
          maxW={{ base: '100vw', sm: '90vw', md: '600px' }}
          onClick={() => setIsDialogOpen(false)}
          cursor="pointer"
        >
          <DialogHeader>Cartón Escaneado #{scannedTicket?.id}</DialogHeader>
          <DialogCloseTrigger />
          <DialogBody pb={6} overflowX="auto">
            {scannedTicket && (
              <TicketDisplay ticket={scannedTicket} calledNumbers={calledNumbers} />
            )}
          </DialogBody>
        </DialogContent>
      </DialogRoot>

      <Toaster />
    </Container>
  );
}

export default App;
