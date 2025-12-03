/**
 * Tools Page - Redirects to chat with tools sidebar
 * Tools are now accessible via the side navbar in MainChat
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Tools() {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to chat page where tools sidebar is available
    navigate('/chat', { replace: true });
  }, [navigate]);

  return (
    <div className="h-screen flex items-center justify-center bg-light-bg dark:bg-dark-bg">
      <div className="text-center">
        <p className="text-gray-600 dark:text-dark-text-secondary">Redirecting to chat...</p>
      </div>
    </div>
  );
}

