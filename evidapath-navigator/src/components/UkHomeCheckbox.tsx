// Asked only of British and Irish citizens: UK "Home" fees depend on where
// you've lived, not on your passport.
export function UkHomeCheckbox({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="mt-3 flex items-start gap-2 text-sm text-foreground cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 h-4 w-4 accent-primary"
      />
      <span>
        I've lived in the UK for the last 3 years
        <span className="block text-xs text-muted-foreground">
          UK universities then charge the Home fee (£10,050 a year from 2027) instead of the
          international one.
        </span>
      </span>
    </label>
  );
}
