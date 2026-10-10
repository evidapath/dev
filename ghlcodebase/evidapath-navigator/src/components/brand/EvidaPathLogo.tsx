import type { ImgHTMLAttributes } from "react";

export const EVIDAPATH_HORIZONTAL_LOGO_URL =
  "https://vibe.filesafe.space/1790101091506917993/attachments/97f9ed1b-deaf-4b63-b9a8-4b2e1801ea23.png";

export const EVIDAPATH_ICON_URL =
  "https://vibe.filesafe.space/1790101091506917993/attachments/42806b48-2493-4ff4-ac73-5110d9c6ec2b.png";

interface BrandImageProps extends ImgHTMLAttributes<HTMLImageElement> {
  size?: number;
  height?: number;
}

/**
 * Official EvidaPath leaf/path brand emblem icon (square)
 */
export function EvidaPathMark({
  size = 32,
  className = "",
  alt = "EvidaPath emblem",
  ...props
}: BrandImageProps) {
  return (
    <img
      src={EVIDAPATH_ICON_URL}
      alt={alt}
      width={size}
      height={size}
      className={`shrink-0 object-contain ${className}`}
      style={{ width: `${size}px`, height: `${size}px` }}
      loading="eager"
      {...props}
    />
  );
}

interface LogoProps extends BrandImageProps {
  showText?: boolean;
}

/**
 * Official EvidaPath horizontal brand logo (emblem + wordmark)
 */
export function EvidaPathLogo({
  height = 36,
  size,
  className = "",
  alt = "EvidaPath — Education Decision Intelligence",
  ...props
}: LogoProps) {
  const finalHeight = size ?? height;
  return (
    <div className={`inline-flex items-center ${className}`}>
      <img
        src={EVIDAPATH_HORIZONTAL_LOGO_URL}
        alt={alt}
        height={finalHeight}
        className="h-auto object-contain max-w-[200px] sm:max-w-[240px]"
        style={{ height: `${finalHeight}px` }}
        loading="eager"
        {...props}
      />
    </div>
  );
}
