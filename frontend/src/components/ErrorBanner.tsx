interface ErrorBannerProps {
  message: string;
  onDismiss: () => void;
}

export default function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
  return (
    <div className="alert fade-in" role="alert">
      <span className="alert__icon" aria-hidden="true">
        !
      </span>
      <p className="alert__text">{message}</p>
      <button
        type="button"
        className="alert__close"
        aria-label="Dismiss message"
        onClick={onDismiss}
      >
        ×
      </button>
    </div>
  );
}
