import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LikeButton from './LikeButton';
import { apiClient, getToken } from '@/lib/api';

// Mock the API client and getToken
jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
  getToken: jest.fn(),
}));

describe('LikeButton', () => {
  const mockApiClient = apiClient as jest.MockedFunction<typeof apiClient>;
  const mockGetToken = getToken as jest.MockedFunction<typeof getToken>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockGetToken.mockReturnValue('mock-token');
  });

  it('renders with initial likes count', () => {
    render(
      <LikeButton
        recipeId={1}
        initialLikesCount={5}
        initialLiked={false}
      />
    );

    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('shows filled heart when liked', () => {
    render(
      <LikeButton
        recipeId={1}
        initialLikesCount={5}
        initialLiked={true}
      />
    );

    const button = screen.getByRole('button');
    const svg = button.querySelector('svg');
    expect(svg).toHaveClass('fill-current');
  });

  it('toggles like when clicked', async () => {
    mockApiClient.mockResolvedValueOnce({
      liked: true,
      likes_count: 6,
    });

    render(
      <LikeButton
        recipeId={1}
        initialLikesCount={5}
        initialLiked={false}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockApiClient).toHaveBeenCalledWith(
        '/api/recipes/1/like',
        expect.objectContaining({
          method: 'POST',
          requiresAuth: true,
        })
      );
    });

    await waitFor(() => {
      expect(screen.getByText('6')).toBeInTheDocument();
    });
  });

  it('toggles unlike when clicked on liked recipe', async () => {
    mockApiClient.mockResolvedValueOnce({
      liked: false,
      likes_count: 4,
    });

    render(
      <LikeButton
        recipeId={1}
        initialLikesCount={5}
        initialLiked={true}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockApiClient).toHaveBeenCalledWith(
        '/api/recipes/1/like',
        expect.objectContaining({
          method: 'DELETE',
          requiresAuth: true,
        })
      );
    });

    await waitFor(() => {
      expect(screen.getByText('4')).toBeInTheDocument();
    });
  });

  it('shows alert when not authenticated', () => {
    mockGetToken.mockReturnValue(null);
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

    render(
      <LikeButton
        recipeId={1}
        initialLikesCount={5}
        initialLiked={false}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(alertSpy).toHaveBeenCalledWith('Please log in to like recipes');
    expect(mockApiClient).not.toHaveBeenCalled();

    alertSpy.mockRestore();
  });

  it('disables button while loading', async () => {
    mockApiClient.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ liked: true, likes_count: 6 }), 100))
    );

    render(
      <LikeButton
        recipeId={1}
        initialLikesCount={5}
        initialLiked={false}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(button).toBeDisabled();

    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });
});
