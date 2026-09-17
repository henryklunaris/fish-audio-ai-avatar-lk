import { Button } from '@/components/ui/button';

const STACK = [
  { name: 'Fish Audio', role: 'expressive voice', href: 'https://fish.audio' },
  { name: 'Tavus', role: 'realistic face', href: 'https://tavus.io' },
  { name: 'LiveKit', role: 'realtime pipeline', href: 'https://livekit.io' },
];

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center px-6 text-center">
        <p className="text-muted-foreground mb-3 font-mono text-xs font-bold tracking-wider uppercase">
          Meet Coral
        </p>
        <h1 className="text-foreground max-w-xl text-3xl leading-tight font-semibold text-balance md:text-5xl">
          An AI avatar that sounds like it means it.
        </h1>
        <p className="text-muted-foreground mt-4 max-w-md leading-6 text-pretty">
          Coral whispers, laughs, gets excited and calms down mid-conversation. Her voice is Fish
          Audio S2.1 Pro, her face is Tavus, and the whole thing runs live on LiveKit.
        </p>

        <Button
          size="lg"
          onClick={onStartCall}
          className="mt-8 w-64 rounded-full font-mono text-xs font-bold tracking-wider uppercase"
        >
          {startButtonText}
        </Button>

        <ul className="mt-10 flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
          {STACK.map((s) => (
            <li key={s.name} className="flex flex-col items-center">
              <a
                target="_blank"
                rel="noopener noreferrer"
                href={s.href}
                className="text-foreground font-mono text-xs font-bold tracking-wider uppercase underline-offset-4 hover:underline"
              >
                {s.name}
              </a>
              <span className="text-muted-foreground text-xs">{s.role}</span>
            </li>
          ))}
        </ul>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Try: &ldquo;Whisper me a secret&rdquo;, &ldquo;Tell me a joke&rdquo;, or &ldquo;I just got
          the job!&rdquo;
        </p>
      </div>
    </div>
  );
};
