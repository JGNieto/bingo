import React, { useEffect, useRef, useState } from 'react';
import { Box, Button, Text, Stack } from '@chakra-ui/react';
import { Html5Qrcode } from 'html5-qrcode';
import { toaster } from './ui/toaster';
import { TicketData } from '../App';

interface QRScannerProps {
  onScan: (data: TicketData) => void;
}

const QRScanner: React.FC<QRScannerProps> = ({ onScan }) => {
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef<Html5Qrcode | null>(null);

  const parseQRData = (qrData: string): TicketData | null => {
    try {
      // Convert the string to a Uint8Array
      // The QR code should contain binary data
      const binaryData = new Uint8Array(qrData.length);
      for (let i = 0; i < qrData.length; i++) {
        binaryData[i] = qrData.charCodeAt(i);
      }

      // Check if we have at least 29 bytes (2 for ID + 27 for numbers)
      if (binaryData.length < 29) {
        throw new Error('Invalid QR code format: insufficient data');
      }

      // First 2 bytes are the ticket ID (little endian)
      const id = binaryData[0] | (binaryData[1] << 8);

      // Next 27 bytes are the ticket numbers
      const numbers: number[] = [];
      for (let i = 2; i < 29; i++) {
        numbers.push(binaryData[i]);
      }

      return { id, numbers };
    } catch (error) {
      console.error('Error parsing QR data:', error);
      return null;
    }
  };

  const startScanning = async () => {
    try {
      // First, request camera permission explicitly for Safari
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }
        });
        // Stop the test stream immediately
        stream.getTracks().forEach(track => track.stop());
      } catch (permError) {
        console.error('Camera permission error:', permError);
        toaster.create({
          title: 'Camera Permission Denied',
          description: 'Please allow camera access in your browser settings.',
          type: 'error',
          duration: 5000,
        });
        return;
      }

      const scanner = new Html5Qrcode('qr-reader');
      scannerRef.current = scanner;

      // Get available cameras
      const devices = await Html5Qrcode.getCameras();
      if (!devices || devices.length === 0) {
        throw new Error('No cameras found');
      }

      // Find rear camera or use first available
      const rearCamera = devices.find(device =>
        device.label.toLowerCase().includes('back') ||
        device.label.toLowerCase().includes('rear')
      ) || devices[devices.length - 1];

      await scanner.start(
        rearCamera.id,
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0,
        },
        (decodedText) => {
          const ticketData = parseQRData(decodedText);
          if (ticketData) {
            onScan(ticketData);
            stopScanning();
            toaster.create({
              title: 'Ticket scanned',
              description: `Ticket #${ticketData.id} has been scanned`,
              type: 'success',
              duration: 2000,
            });
          } else {
            toaster.create({
              title: 'Invalid QR code',
              description: 'The scanned QR code is not a valid bingo ticket',
              type: 'error',
              duration: 2000,
            });
          }
        },
        (errorMessage) => {
          // Ignore scanning errors (they happen constantly while scanning)
        }
      );

      setIsScanning(true);
    } catch (error) {
      console.error('Error starting scanner:', error);
      let errorMessage = 'Unable to access camera. ';

      if (error instanceof Error) {
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
          errorMessage += 'Please allow camera access in your browser settings.';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
          errorMessage += 'No camera found on this device.';
        } else if (error.name === 'NotReadableError') {
          errorMessage += 'Camera is already in use by another application.';
        } else if (error.name === 'SecurityError') {
          errorMessage += 'Camera access requires HTTPS connection.';
        } else {
          errorMessage += error.message || 'Please check permissions.';
        }
      }

      toaster.create({
        title: 'Camera Error',
        description: errorMessage,
        type: 'error',
        duration: 5000,
      });
    }
  };

  const stopScanning = async () => {
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop();
        scannerRef.current.clear();
        scannerRef.current = null;
        setIsScanning(false);
      } catch (error) {
        console.error('Error stopping scanner:', error);
      }
    }
  };

  useEffect(() => {
    return () => {
      if (scannerRef.current) {
        scannerRef.current.stop().catch(console.error);
      }
    };
  }, []);

  return (
    <Stack gap={4} align="stretch">
      <Box
        id="qr-reader"
        width="100%"
        minH={isScanning ? '300px' : '0'}
        borderRadius="md"
        overflow="hidden"
      />

      {!isScanning ? (
        <Box textAlign="center">
          <Text mb={4} color="gray.600">
            Scan a bingo ticket QR code to view the ticket
          </Text>
          <Button colorScheme="blue" size="lg" onClick={startScanning}>
            Start Camera
          </Button>
        </Box>
      ) : (
        <Button colorScheme="red" onClick={stopScanning}>
          Stop Scanning
        </Button>
      )}

      <Box
        p={4}
        bg="blue.50"
        borderRadius="md"
        border="1px solid"
        borderColor="blue.200"
      >
        <Text fontSize="sm" color="blue.700">
          <strong>Note:</strong> Point your camera at a bingo ticket QR code to scan it.
          The ticket will be displayed with called numbers highlighted.
        </Text>
      </Box>
    </Stack>
  );
};

export default QRScanner;
