/**
 * Component tests for ChatInterface
 * RED PHASE: These tests should FAIL until the component is implemented
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatInterface from '../../src/components/ChatInterface';

// Mock fetch
global.fetch = jest.fn();

describe('ChatInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders chat interface with input field', () => {
    render(<ChatInterface userId="test-user-id" />);

    // Should have a text input for messages
    const input = screen.getByPlaceholderText(/type a message/i);
    expect(input).toBeInTheDocument();
  });

  it('renders send button', () => {
    render(<ChatInterface userId="test-user-id" />);

    // Should have a send button
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeInTheDocument();
  });

  it('sends message when send button is clicked', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'Task created successfully',
        conversation_id: 'conv-123'
      })
    });

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Type a message
    fireEvent.change(input, { target: { value: 'Add a task to buy groceries' } });

    // Click send
    fireEvent.click(sendButton);

    // Should call API
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/test-user-id/chat'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: expect.stringContaining('Add a task to buy groceries')
        })
      );
    });
  });

  it('displays user message immediately (optimistic update)', async () => {
    (global.fetch as jest.Mock).mockImplementation(() =>
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({
          response: 'Task created',
          conversation_id: 'conv-123'
        })
      }), 100))
    );

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Type and send message
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);

    // User message should appear immediately
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('displays assistant response after API call', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'Task created successfully',
        conversation_id: 'conv-123'
      })
    });

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Add a task' } });
    fireEvent.click(sendButton);

    // Wait for assistant response
    await waitFor(() => {
      expect(screen.getByText('Task created successfully')).toBeInTheDocument();
    });
  });

  it('clears input field after sending message', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'Response',
        conversation_id: 'conv-123'
      })
    });

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i) as HTMLInputElement;
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    // Input should be cleared
    await waitFor(() => {
      expect(input.value).toBe('');
    });
  });

  it('shows loading indicator while waiting for response', async () => {
    (global.fetch as jest.Mock).mockImplementation(() =>
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({
          response: 'Response',
          conversation_id: 'conv-123'
        })
      }), 100))
    );

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(sendButton);

    // Should show loading indicator
    expect(screen.getByText(/typing|loading|thinking/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(sendButton);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/error|failed|try again/i)).toBeInTheDocument();
    });
  });

  it('removes optimistic message on error (rollback)', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('API error'));

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    // Message appears optimistically
    expect(screen.getByText('Test message')).toBeInTheDocument();

    // After error, optimistic message should be removed
    await waitFor(() => {
      expect(screen.queryByText('Test message')).not.toBeInTheDocument();
    });
  });

  it('disables send button while sending', async () => {
    (global.fetch as jest.Mock).mockImplementation(() =>
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({
          response: 'Response',
          conversation_id: 'conv-123'
        })
      }), 100))
    );

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(sendButton);

    // Button should be disabled
    expect(sendButton).toBeDisabled();

    // After response, button should be enabled again
    await waitFor(() => {
      expect(sendButton).not.toBeDisabled();
    });
  });

  it('maintains conversation ID across messages', async () => {
    const conversationId = 'conv-123';

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          response: 'First response',
          conversation_id: conversationId
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          response: 'Second response',
          conversation_id: conversationId
        })
      });

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Send first message
    fireEvent.change(input, { target: { value: 'First message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('First response')).toBeInTheDocument();
    });

    // Send second message
    fireEvent.change(input, { target: { value: 'Second message' } });
    fireEvent.click(sendButton);

    // Second request should include conversation_id
    await waitFor(() => {
      expect(global.fetch).toHaveBeenLastCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: expect.stringContaining(conversationId)
        })
      );
    });
  });

  it('prevents sending empty messages', () => {
    render(<ChatInterface userId="test-user-id" />);

    const sendButton = screen.getByRole('button', { name: /send/i });

    // Send button should be disabled when input is empty
    expect(sendButton).toBeDisabled();
  });

  it('allows sending message with Enter key', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'Response',
        conversation_id: 'conv-123'
      })
    });

    render(<ChatInterface userId="test-user-id" />);

    const input = screen.getByPlaceholderText(/type a message/i);

    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

    // Should send message
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
