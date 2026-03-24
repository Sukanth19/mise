import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FollowButton from './FollowButton';
import LikeButton from './LikeButton';
import CommentForm from './CommentForm';
import ShareButtons from './ShareButtons';
import { apiClient, getToken } from '@/lib/api';

// Mock the API client and getToken
jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
  getToken: jest.fn(),
}));

const mockApiClient = apiClient as jest.MockedFunction<typeof apiClient>;
const mockGetToken = getToken as jest.MockedFunction<typeof getToken>;

describe('FollowButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetToken.mockReturnValue('mock-token');
  });

  it('should render with initial state', () => {
    render(
      <FollowButton
        userId={1}
        initialFollowersCount={10}
        initialFollowing={false}
      />
    );

    expect(screen.getByText('Follow')).toBeInTheDocument();
  });

  it('should toggle follow state when clicked', async () => {
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

  it('should toggle unfollow state when clicked', async () => {
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

  it('should show loading state while toggling', async () => {
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
  });
});

describe('LikeButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetToken.mockReturnValue('mock-token');
    // Mock window.alert
    global.alert = jest.fn();
  });

  it('should render with initial state', () => {
    render(
      <LikeButton
        recipeId={1}
        initialLikesCount={5}
        initialLiked={false}
      />
    );

    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('should toggle like state when clicked', async () => {
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

  it('should toggle unlike state when clicked', async () => {
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

  it('should show alert when not authenticated', () => {
    mockGetToken.mockReturnValue(null);

    render(
      <LikeButton
        recipeId={1}
        initialLikesCount={5}
        initialLiked={false}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(global.alert).toHaveBeenCalledWith('Please log in to like recipes');
  });
});

describe('CommentForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetToken.mockReturnValue('mock-token');
  });

  it('should render comment form', () => {
    const mockOnCommentAdded = jest.fn();
    render(<CommentForm recipeId={1} onCommentAdded={mockOnCommentAdded} />);

    expect(screen.getByPlaceholderText('Add a comment...')).toBeInTheDocument();
    expect(screen.getByText('Post Comment')).toBeInTheDocument();
  });

  it('should submit comment when form is submitted', async () => {
    const mockComment = {
      id: 1,
      recipe_id: 1,
      user_id: 1,
      comment_text: 'Great recipe!',
      created_at: new Date().toISOString(),
      author: {
        id: 1,
        username: 'testuser',
      },
    };

    mockApiClient.mockResolvedValueOnce(mockComment);

    const mockOnCommentAdded = jest.fn();
    render(<CommentForm recipeId={1} onCommentAdded={mockOnCommentAdded} />);

    const textarea = screen.getByPlaceholderText('Add a comment...');
    const submitButton = screen.getByText('Post Comment');

    fireEvent.change(textarea, { target: { value: 'Great recipe!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApiClient).toHaveBeenCalledWith(
        '/api/recipes/1/comments',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ comment_text: 'Great recipe!' }),
          requiresAuth: true,
        })
      );
    });

    await waitFor(() => {
      expect(mockOnCommentAdded).toHaveBeenCalledWith(mockComment);
    });

    // Check that textarea is cleared after submission
    expect(textarea).toHaveValue('');
  });

  it('should disable submit button when comment is empty', () => {
    const mockOnCommentAdded = jest.fn();
    render(<CommentForm recipeId={1} onCommentAdded={mockOnCommentAdded} />);

    // The button should be disabled when textarea is empty
    const submitButton = screen.getByText('Post Comment');
    expect(submitButton).toBeDisabled();
  });

  it('should show error when not authenticated', async () => {
    mockGetToken.mockReturnValue(null);

    const mockOnCommentAdded = jest.fn();
    render(<CommentForm recipeId={1} onCommentAdded={mockOnCommentAdded} />);

    const textarea = screen.getByPlaceholderText('Add a comment...');
    const submitButton = screen.getByText('Post Comment');

    fireEvent.change(textarea, { target: { value: 'Great recipe!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Please log in to comment')).toBeInTheDocument();
    });

    expect(mockApiClient).not.toHaveBeenCalled();
  });
});

describe('ShareButtons', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockApiClient.mockResolvedValue({
      title: 'Test Recipe',
      description: 'A delicious test recipe',
      image_url: 'https://example.com/image.jpg',
      url: 'https://example.com/recipes/1',
    });

    // Mock navigator.clipboard
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined),
      },
    });

    // Mock window.open
    global.open = jest.fn();
  });

  it('should render share buttons', async () => {
    render(<ShareButtons recipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Share this recipe')).toBeInTheDocument();
    });

    expect(screen.getByText('Copy Link')).toBeInTheDocument();
    expect(screen.getByText('Twitter')).toBeInTheDocument();
    expect(screen.getByText('Facebook')).toBeInTheDocument();
    expect(screen.getByText('Pinterest')).toBeInTheDocument();
  });

  it('should copy link to clipboard when copy button is clicked', async () => {
    render(<ShareButtons recipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Copy Link')).toBeInTheDocument();
    });

    const copyButton = screen.getByText('Copy Link');
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('https://example.com/recipes/1');
    });

    await waitFor(() => {
      expect(screen.getByText('Copied!')).toBeInTheDocument();
    });
  });

  it('should generate correct Twitter share URL', async () => {
    render(<ShareButtons recipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Twitter')).toBeInTheDocument();
    });

    const twitterButton = screen.getByText('Twitter');
    fireEvent.click(twitterButton);

    expect(global.open).toHaveBeenCalledWith(
      expect.stringContaining('twitter.com/intent/tweet'),
      '_blank',
      'width=550,height=420'
    );
  });

  it('should generate correct Facebook share URL', async () => {
    render(<ShareButtons recipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Facebook')).toBeInTheDocument();
    });

    const facebookButton = screen.getByText('Facebook');
    fireEvent.click(facebookButton);

    expect(global.open).toHaveBeenCalledWith(
      expect.stringContaining('facebook.com/sharer'),
      '_blank',
      'width=550,height=420'
    );
  });

  it('should generate correct Pinterest share URL', async () => {
    render(<ShareButtons recipeId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Pinterest')).toBeInTheDocument();
    });

    const pinterestButton = screen.getByText('Pinterest');
    fireEvent.click(pinterestButton);

    expect(global.open).toHaveBeenCalledWith(
      expect.stringContaining('pinterest.com/pin/create'),
      '_blank',
      'width=750,height=550'
    );
  });
});
