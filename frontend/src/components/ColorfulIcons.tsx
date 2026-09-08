export const ColorfulSun = ({
  size = 32,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
  >
    <circle
      cx="12"
      cy="12"
      r="5"
      fill="#facc15"
      stroke="#eab308"
      strokeWidth="2"
    />
    <path
      d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
      stroke="#eab308"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

export const ColorfulCloudSun = ({
  size = 32,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
  >
    <circle
      cx="17"
      cy="9"
      r="4"
      fill="#facc15"
      stroke="#eab308"
      strokeWidth="2"
    />
    <path
      d="M17 2v2M23 9h-2M20.5 4.5l-1.5 1.5"
      stroke="#eab308"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M7 18a4 4 0 0 1-1.5-7.7 5 5 0 0 1 9 1 3.5 3.5 0 0 1 1.5 6.7"
      fill="#d1d5db"
      stroke="#9ca3af"
      strokeWidth="2"
      strokeLinejoin="round"
    />
    <path
      d="M16 18H5.5a4.5 4.5 0 0 1 0-9 5.5 5.5 0 0 1 10.5 0A3.5 3.5 0 0 1 16 18z"
      fill="#e5e7eb"
      stroke="#9ca3af"
      strokeWidth="2"
      strokeLinejoin="round"
    />
  </svg>
);

export const ColorfulCloudRain = ({
  size = 32,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
  >
    <path
      d="M7 16a4 4 0 0 1-1.5-7.7 5 5 0 0 1 9 1 3.5 3.5 0 0 1 1.5 6.7"
      fill="#d1d5db"
      stroke="#9ca3af"
      strokeWidth="2"
      strokeLinejoin="round"
    />
    <path
      d="M16 16H5.5a4.5 4.5 0 0 1 0-9 5.5 5.5 0 0 1 10.5 0A3.5 3.5 0 0 1 16 16z"
      fill="#e5e7eb"
      stroke="#9ca3af"
      strokeWidth="2"
      strokeLinejoin="round"
    />
    <path
      d="M8 20l1 2M12 20l1 2M16 20l1 2"
      stroke="#3b82f6"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

export const ColorfulDroplet = ({
  size = 32,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
  >
    <path
      d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"
      fill="#bfdbfe"
      stroke="#3b82f6"
      strokeWidth="2"
      strokeLinejoin="round"
    />
  </svg>
);

export const ColorfulWind = ({
  size = 32,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
  >
    <path
      d="M12.8 19.6A2 2 0 1 0 14 16H2"
      stroke="#14b8a6"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M17.5 8a2.5 2.5 0 1 1 2 4H2"
      stroke="#0ea5e9"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M9.8 4.4A2 2 0 1 1 11 8H2"
      stroke="#8b5cf6"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const ColorfulChartIcon = ({
  size = 32,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <rect x="3" y="12" width="4" height="8" fill="#93c5fd" stroke="#3b82f6" />
    <path d="M7 12V10h4v2" stroke="#3b82f6" />
    <rect x="10" y="6" width="4" height="14" fill="#a78bfa" stroke="#8b5cf6" />
    <rect x="17" y="10" width="4" height="10" fill="#fca5a5" stroke="#ef4444" />
    <path d="M17 10V8h4v2" stroke="#ef4444" />
  </svg>
);

export const ColorfulAqiIcon = ({
  size = 30,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    aria-hidden="true"
    className={className}
  >
    <rect x="5" y="14" width="5" height="11" rx="1.5" fill="#3B82F6" />
    <rect x="13.5" y="9" width="5" height="16" rx="1.5" fill="#8B5CF6" />
    <rect x="22" y="5" width="5" height="20" rx="1.5" fill="#F43F5E" />
  </svg>
);

export const ColorfulPm25Icon = ({
  size = 30,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    aria-hidden="true"
    className={className}
  >
    <circle cx="9" cy="10" r="3" fill="#3B82F6" />
    <circle cx="17" cy="7" r="2.5" fill="#8B5CF6" />
    <circle cx="24" cy="12" r="3" fill="#F43F5E" />
    <circle cx="13" cy="18" r="2.5" fill="#06B6D4" />
    <circle cx="22" cy="20" r="2.5" fill="#8B5CF6" />
    <circle cx="8" cy="25" r="2.5" fill="#3B82F6" />
    <circle cx="17" cy="27" r="2.5" fill="#F43F5E" />
    <circle cx="26" cy="27" r="2" fill="#06B6D4" />
  </svg>
);

export const ColorfulPm10Icon = ({
  size = 30,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    aria-hidden="true"
    className={className}
  >
    <circle cx="9" cy="9" r="4" fill="#3B82F6" />
    <circle cx="21" cy="9" r="4" fill="#8B5CF6" />
    <circle cx="15" cy="18" r="4" fill="#F43F5E" />
    <circle cx="25" cy="21" r="3.5" fill="#06B6D4" />
    <circle cx="7" cy="24" r="3.5" fill="#8B5CF6" />
  </svg>
);

export const ColorfulTemperatureIcon = ({
  size = 30,
  className = "",
}: {
  size?: number;
  className?: string;
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    aria-hidden="true"
    className={className}
  >
    <path
      d="M16 6a5 5 0 0 0-5 5v9.5a7 7 0 1 0 10 0V11a5 5 0 0 0-5-5Z"
      fill="#3B82F6"
    />
    <path d="M16 16v7" stroke="#F43F5E" strokeWidth="3" strokeLinecap="round" />
    <circle cx="16" cy="25" r="3.5" fill="#F43F5E" />
  </svg>
);

export const ColorfulBuildingIcon = ({ size = 30, className = "" }: { size?: number, className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true" className={className}>
    <rect x="6" y="10" width="8" height="18" rx="1" fill="#3B82F6" />
    <rect x="16" y="4" width="10" height="24" rx="1" fill="#8B5CF6" />
    <rect x="8" y="14" width="2" height="2" fill="#fff" opacity="0.6" />
    <rect x="8" y="18" width="2" height="2" fill="#fff" opacity="0.6" />
    <rect x="8" y="22" width="2" height="2" fill="#fff" opacity="0.6" />
    <rect x="18" y="8" width="2" height="2" fill="#fff" opacity="0.6" />
    <rect x="22" y="8" width="2" height="2" fill="#fff" opacity="0.6" />
    <rect x="18" y="14" width="2" height="2" fill="#fff" opacity="0.6" />
    <rect x="22" y="14" width="2" height="2" fill="#fff" opacity="0.6" />
    <rect x="18" y="20" width="2" height="2" fill="#fff" opacity="0.6" />
    <rect x="22" y="20" width="2" height="2" fill="#fff" opacity="0.6" />
  </svg>
);

