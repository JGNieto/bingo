import React from 'react';
import { Box, Grid, GridItem, Text, Stack } from '@chakra-ui/react';
import { TicketData } from '../App';

interface TicketDisplayProps {
  ticket: TicketData;
  calledNumbers: Set<number>;
}

const TicketDisplay: React.FC<TicketDisplayProps> = ({ ticket, calledNumbers }) => {
  // Convert the flat array of 27 numbers into a 3x9 grid
  const rows: number[][] = [];
  for (let i = 0; i < 3; i++) {
    rows.push(ticket.numbers.slice(i * 9, (i + 1) * 9));
  }

  // Check if a row is complete (all non-zero numbers have been called)
  const isRowComplete = (row: number[]): boolean => {
    const numbersInRow = row.filter(n => n !== 0);
    if (numbersInRow.length === 0) return false;
    return numbersInRow.every(n => calledNumbers.has(n));
  };

  const rowCompletionStatus = rows.map(isRowComplete);
  const completedRowsCount = rowCompletionStatus.filter(Boolean).length;

  return (
    <Stack gap={4} align="stretch">
      {completedRowsCount > 0 && (
        <Box
          p={3}
          bg="yellow.100"
          borderRadius="md"
          border="2px solid"
          borderColor="yellow.400"
          textAlign="center"
        >
          <Text fontWeight="bold" color="yellow.800">
            {completedRowsCount === 3
              ? 'FULL HOUSE! 🎉'
              : `${completedRowsCount} ${completedRowsCount === 1 ? 'Line' : 'Lines'} Complete!`}
          </Text>
        </Box>
      )}

      <Box
        border="3px solid"
        borderColor="gray.800"
        borderRadius="lg"
        overflow="hidden"
        bg="white"
      >
        {rows.map((row, rowIndex) => {
          const isComplete = rowCompletionStatus[rowIndex];
          return (
            <Box
              key={rowIndex}
              borderBottom={rowIndex < 2 ? '2px solid' : 'none'}
              borderColor="gray.800"
              bg={isComplete ? 'yellow.50' : 'white'}
            >
              <Grid templateColumns="repeat(9, 1fr)" gap={0}>
                {row.map((num, colIndex) => {
                  const isEmpty = num === 0;
                  const isCalled = !isEmpty && calledNumbers.has(num);

                  return (
                    <GridItem
                      key={colIndex}
                      borderRight={colIndex < 8 ? '1px solid' : 'none'}
                      borderColor="gray.400"
                    >
                      <Box
                        p={{ base: 1, sm: 2, md: 3 }}
                        minH={{ base: '35px', sm: '40px', md: '50px' }}
                        minW={{ base: '35px', sm: '40px', md: '50px' }}
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        bg={
                          isEmpty
                            ? 'gray.100'
                            : isCalled
                            ? isComplete
                              ? 'orange.400'
                              : 'green.400'
                            : 'white'
                        }
                        color={
                          isEmpty
                            ? 'gray.400'
                            : isCalled
                            ? 'white'
                            : 'gray.800'
                        }
                        fontWeight={isCalled ? 'bold' : 'normal'}
                        fontSize={{ base: 'sm', sm: 'md', md: 'lg' }}
                        position="relative"
                      >
                        <Text>{isEmpty ? '-' : num}</Text>
                      </Box>
                    </GridItem>
                  );
                })}
              </Grid>
            </Box>
          );
        })}
      </Box>

      <Box
        p={3}
        bg="gray.50"
        borderRadius="md"
        border="1px solid"
        borderColor="gray.200"
      >
        <Text fontSize="sm" color="gray.700">
          <strong>Legend:</strong>
        </Text>
        <Grid templateColumns="repeat(2, 1fr)" gap={2} mt={2}>
          <GridItem>
            <Box display="flex" alignItems="center" gap={2}>
              <Box w="20px" h="20px" bg="green.400" borderRadius="sm" />
              <Text fontSize="sm">Called number</Text>
            </Box>
          </GridItem>
          <GridItem>
            <Box display="flex" alignItems="center" gap={2}>
              <Box w="20px" h="20px" bg="orange.400" borderRadius="sm" />
              <Text fontSize="sm">Complete line</Text>
            </Box>
          </GridItem>
        </Grid>
      </Box>
    </Stack>
  );
};

export default TicketDisplay;
