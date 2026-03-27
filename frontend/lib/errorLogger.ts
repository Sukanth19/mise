/**
 * Centralized error logging utility for the frontend
 * In production, this could send errors to a logging service like Sentry
 */

export interface ErrorLog {
  message: string;
  stack?: string;
  timestamp: string;
  url: string;
  userAgent: string;
  context?: Record<string, any>;
}

class ErrorLogger {
  private logs: ErrorLog[] = [];
  private maxLogs = 100;

  log(error: Error | string, context?: Record<string, any>): void {
    const errorLog: ErrorLog = {
      message: error instanceof Error ? error.message : error,
      stack: error instanceof Error ? error.stack : undefined,
      timestamp: new Date().toISOString(),
      url: typeof window !== 'undefined' ? window.location.href : '',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      context,
    };

    // Add to in-memory logs
    this.logs.push(errorLog);
    
    // Keep only the most recent logs
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error logged:', errorLog);
    }

    // In production, you would send this to a logging service
    // Example: sendToSentry(errorLog);
  }

  getLogs(): ErrorLog[] {
    return [...this.logs];
  }

  clearLogs(): void {
    this.logs = [];
  }

  // Log API errors with additional context
  logApiError(
    endpoint: string,
    method: string,
    statusCode: number,
    error: Error | string,
    requestData?: any
  ): void {
    this.log(error, {
      type: 'API_ERROR',
      endpoint,
      method,
      statusCode,
      requestData,
    });
  }

  // Log component errors
  logComponentError(
    componentName: string,
    error: Error | string,
    props?: any
  ): void {
    this.log(error, {
      type: 'COMPONENT_ERROR',
      componentName,
      props,
    });
  }

  // Log navigation errors
  logNavigationError(
    from: string,
    to: string,
    error: Error | string
  ): void {
    this.log(error, {
      type: 'NAVIGATION_ERROR',
      from,
      to,
    });
  }
}

// Export singleton instance
export const errorLogger = new ErrorLogger();

// Setup global error handlers
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    errorLogger.log(event.error || event.message, {
      type: 'GLOBAL_ERROR',
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    errorLogger.log(event.reason, {
      type: 'UNHANDLED_PROMISE_REJECTION',
    });
  });
}
