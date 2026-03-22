import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ImageUpload from './ImageUpload';

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('ImageUpload', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders upload area with instructions', () => {
    const mockOnImageUploaded = jest.fn();
    render(<ImageUpload onImageUploaded={mockOnImageUploaded} />);

    expect(screen.getByText(/Click to upload/i)).toBeInTheDocument();
    expect(screen.getByText(/or drag and drop/i)).toBeInTheDocument();
    expect(screen.getByText(/JPEG, PNG, or WebP up to 5MB/i)).toBeInTheDocument();
  });

  it('displays initial image preview when provided', () => {
    const mockOnImageUploaded = jest.fn();
    const initialUrl = 'http://example.com/image.jpg';
    
    render(<ImageUpload onImageUploaded={mockOnImageUploaded} initialImageUrl={initialUrl} />);

    const img = screen.getByAltText('Preview');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', initialUrl);
  });

  it('uploads file and shows preview on successful upload', async () => {
    const mockOnImageUploaded = jest.fn();
    const mockUrl = 'http://example.com/uploaded-image.jpg';
    
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ url: mockUrl }),
    });

    const { container } = render(<ImageUpload onImageUploaded={mockOnImageUploaded} />);

    const file = new File(['image'], 'test.jpg', { type: 'image/jpeg' });
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(mockOnImageUploaded).toHaveBeenCalledWith(mockUrl);
    });

    const img = screen.getByAltText('Preview');
    expect(img).toHaveAttribute('src', mockUrl);
  });

  it('displays error for invalid file type', async () => {
    const mockOnImageUploaded = jest.fn();
    
    const { container } = render(<ImageUpload onImageUploaded={mockOnImageUploaded} />);

    const file = new File(['content'], 'test.txt', { type: 'text/plain' });
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/Invalid file type/i)).toBeInTheDocument();
    });

    expect(mockOnImageUploaded).not.toHaveBeenCalled();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('displays error for file size exceeding 5MB', async () => {
    const mockOnImageUploaded = jest.fn();
    
    const { container } = render(<ImageUpload onImageUploaded={mockOnImageUploaded} />);

    // Create a file larger than 5MB
    const largeFile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' });
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [largeFile] } });

    await waitFor(() => {
      expect(screen.getByText(/File size exceeds 5MB limit/i)).toBeInTheDocument();
    });

    expect(mockOnImageUploaded).not.toHaveBeenCalled();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('displays error when upload fails', async () => {
    const mockOnImageUploaded = jest.fn();
    
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Upload failed' }),
    });

    const { container } = render(<ImageUpload onImageUploaded={mockOnImageUploaded} />);

    const file = new File(['image'], 'test.jpg', { type: 'image/jpeg' });
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/Upload failed/i)).toBeInTheDocument();
    });

    expect(mockOnImageUploaded).not.toHaveBeenCalled();
  });

  it('shows uploading state during upload', async () => {
    const mockOnImageUploaded = jest.fn();
    
    let resolveUpload: (value: any) => void;
    const uploadPromise = new Promise((resolve) => {
      resolveUpload = resolve;
    });

    (global.fetch as jest.Mock).mockReturnValueOnce(uploadPromise);

    const { container } = render(<ImageUpload onImageUploaded={mockOnImageUploaded} />);

    const file = new File(['image'], 'test.jpg', { type: 'image/jpeg' });
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/Uploading.../i)).toBeInTheDocument();
    });

    // Resolve the upload
    resolveUpload!({
      ok: true,
      json: async () => ({ url: 'http://example.com/image.jpg' }),
    });

    await waitFor(() => {
      expect(screen.queryByText(/Uploading.../i)).not.toBeInTheDocument();
    });
  });

  it('handles drag and drop', async () => {
    const mockOnImageUploaded = jest.fn();
    const mockUrl = 'http://example.com/dropped-image.jpg';
    
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ url: mockUrl }),
    });

    const { container } = render(<ImageUpload onImageUploaded={mockOnImageUploaded} />);

    const dropZone = container.querySelector('.cursor-pointer') as HTMLElement;
    const file = new File(['image'], 'test.jpg', { type: 'image/jpeg' });

    // Simulate drag enter
    fireEvent.dragEnter(dropZone, {
      dataTransfer: { files: [file] },
    });

    // Simulate drop
    fireEvent.drop(dropZone, {
      dataTransfer: { files: [file] },
    });

    await waitFor(() => {
      expect(mockOnImageUploaded).toHaveBeenCalledWith(mockUrl);
    });
  });

  it('accepts valid image formats', async () => {
    const mockOnImageUploaded = jest.fn();
    
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ url: 'http://example.com/image.jpg' }),
    });

    const { container } = render(<ImageUpload onImageUploaded={mockOnImageUploaded} />);

    const input = container.querySelector('input[type="file"]') as HTMLInputElement;

    // Test JPEG
    const jpegFile = new File(['image'], 'test.jpg', { type: 'image/jpeg' });
    fireEvent.change(input, { target: { files: [jpegFile] } });
    await waitFor(() => expect(mockOnImageUploaded).toHaveBeenCalled());

    jest.clearAllMocks();

    // Test PNG
    const pngFile = new File(['image'], 'test.png', { type: 'image/png' });
    fireEvent.change(input, { target: { files: [pngFile] } });
    await waitFor(() => expect(mockOnImageUploaded).toHaveBeenCalled());

    jest.clearAllMocks();

    // Test WebP
    const webpFile = new File(['image'], 'test.webp', { type: 'image/webp' });
    fireEvent.change(input, { target: { files: [webpFile] } });
    await waitFor(() => expect(mockOnImageUploaded).toHaveBeenCalled());
  });
});
