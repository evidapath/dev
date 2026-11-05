import { useState } from "react";
import { Check, ChevronDown } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "./ui/command";
import { cn } from "@/lib/utils";

// Every typed word has to appear in the name or keywords ("ucl", "toronto", "canada").
// cmdk's default fuzzy match is too loose: "canada" also matched "Khalifa … Technology".
function matches(_value: string, search: string, keywords: string[] = []) {
  const text = keywords.join(" ").toLowerCase();
  return search
    .toLowerCase()
    .split(/\s+/)
    .every((w) => text.includes(w))
    ? 1
    : 0;
}

export interface SearchOption {
  value: string;
  label: string;
  // Shown before the label (e.g. a flag); not matched when typing.
  prefix?: string;
  // Extra words that should match when typing (e.g. the country).
  keywords?: string[];
  // Shorter text for the closed button (e.g. "USD" while the list says "USD · US dollar").
  short?: string;
  group?: string;
}

// A dropdown the student can type into to filter the list, for long lists such as
// universities. Short fixed lists stay as native <select>s.
export function SearchSelect({
  options,
  value,
  onChange,
  placeholder = "Select…",
  searchPlaceholder = "Type to search…",
  className,
  id,
  "aria-label": ariaLabel,
}: {
  options: SearchOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  className?: string;
  id?: string;
  "aria-label"?: string;
}) {
  const [open, setOpen] = useState(false);
  const current = options.find((o) => o.value === value);
  const groups = [...new Set(options.map((o) => o.group ?? ""))];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          id={id}
          type="button"
          role="combobox"
          aria-expanded={open}
          aria-label={ariaLabel}
          className={cn("flex items-center justify-between gap-2 text-left", className)}
        >
          <span className={cn("truncate", !current && "text-muted-foreground")}>
            {current
              ? `${current.prefix ? `${current.prefix} ` : ""}${current.short ?? current.label}`
              : placeholder}
          </span>
          <ChevronDown className="w-4 h-4 shrink-0 opacity-60" />
        </button>
      </PopoverTrigger>
      <PopoverContent align="start" className="p-0 w-(--radix-popover-trigger-width) min-w-64">
        <Command filter={matches}>
          <CommandInput placeholder={searchPlaceholder} />
          <CommandList>
            <CommandEmpty>No matches.</CommandEmpty>
            {groups.map((g) => (
              <CommandGroup key={g || "_"} heading={g || undefined}>
                {options
                  .filter((o) => (o.group ?? "") === g)
                  .map((o) => (
                    <CommandItem
                      key={o.value}
                      value={o.value}
                      keywords={[o.label, ...(o.keywords ?? [])]}
                      onSelect={() => {
                        onChange(o.value);
                        setOpen(false);
                      }}
                    >
                      {o.prefix && <span>{o.prefix}</span>}
                      <span className="flex-1">{o.label}</span>
                      {o.value === value && <Check className="text-primary" />}
                    </CommandItem>
                  ))}
              </CommandGroup>
            ))}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
