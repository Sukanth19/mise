import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FollowButton from './FollowButton';
import { apiClient } from '@/lib/api';

// Mock the API client
jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
}));

describe('FollowButton', () => {
  const mockApiClient = apiClient as jest.MockedFunction<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with "Follow" text when not following', () => {
    render(
      <FollowButton
        userId={1}
        initialFollowersCount={10}
        initialFollowing={false}
      />
    );

    expect(screen.getByText('Follow')).toBeInTheDocument();
  });

  it('renders with "Following" text when already following', () => {
    render(
      <FollowButton
        userId={1}
        initialFollowersCount={10}
        initialFollowing={true}
      />
    );

    expect(screen.getByText('Following')).toBeInTheDocument();
  });

  it('calls follow API when clicked', async () => {
    mockApiClient.mockResolvedValueOnce({
      following: true,
      followers_count: 11,
    });

    render(
      <FollowButton
        userId={1}
        initialFollowersCount={10}
        initialFollowing={false}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockApiClient).toHaveBeenCalledWith(
        '/api/users/1/follow',
        expect.objectContaining({
          method: 'POST',
          requiresAuth: true,
        })
      );
    });

    await waitFor(() => {
      expect(screen.getByText('Following')).toBeInTheDocument();
    });
  });

  it('calls unfollow API when clicked on followed user', async () => {
    mockApiClient.mockResolvedValueOnce({
      following: false,
      followers_count: 9,
    });

    render(
      <FollowButton
        userId={1}
        initialFollowersCount={10}
        initialFollowing={true}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockApiClient).toHaveBeenCalledWith(
        '/api/users/1/follow',
        expect.objectContaining({
          method: 'DELETE',
          requiresAuth: true,
        })
      );
    });

    await waitFor(() => {
      expect(screen.getByText('Follow')).toBeInTheDocument();
    });
  });

  it('disables button while loading', async () => {
    mockApiClient.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ following: true, followers_count: 11 }), 100))
    );

    render(
      <FollowButton
        userId={1}
        initialFollowersCount={10}
        initialFollowing={false}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(button).toBeDisabled();

    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  it('shows loading state while processing', async () => {
    mockApiClient.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ following: true, followers_count: 11 }), 100))
    );

    render(
      <FollowButton
        userId={1}
        initialFollowersCount={10}
        initialFollowing={false}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(screen.getByText('Following...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Following')).toBeInTheDocument();
    });
  });
});
