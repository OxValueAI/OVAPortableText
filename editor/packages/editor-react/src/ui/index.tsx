import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonTone = "neutral" | "primary" | "danger" | "ghost";

export function Button({
  children,
  tone = "neutral",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { tone?: ButtonTone }) {
  const classes = ["ova-pte-ui-button", `ova-pte-ui-button-${tone}`, className].filter(Boolean).join(" ");
  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}

export function Panel({
  title,
  children,
  className
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={["ova-pte-panel", className].filter(Boolean).join(" ")}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}

export function ToolbarGroup({
  label,
  children,
  compact = false
}: {
  label: string;
  children: ReactNode;
  compact?: boolean;
}) {
  return (
    <div className={compact ? "ova-pte-toolbar-group compact" : "ova-pte-toolbar-group"} aria-label={label}>
      <span className="ova-pte-toolbar-label">{label}</span>
      <div className="ova-pte-toolbar-items">{children}</div>
    </div>
  );
}

export function Badge({ children }: { children: ReactNode }) {
  return <span className="ova-pte-badge">{children}</span>;
}
