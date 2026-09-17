'use client';

import { AnimatePresence, motion } from 'motion/react';
import { type AgentMood, useAgentExpression } from '@livekit/components-react';
import { cn } from '@/lib/shadcn/utils';

// Warm hues for bright moods, cool hues for heavy ones
const MOOD_COLORS: Record<AgentMood, string> = {
  angry: '#F5222D',
  excited: '#FF7A45',
  happy: '#FFC53D',
  playful: '#F759AB',
  surprised: '#B37FEB',
  anxious: '#D46B08',
  hopeful: '#52C41A',
  empathetic: '#36CFC9',
  curious: '#6600FF',
  sad: '#2F54EB',
  calm: '#1FD5F9',
};

interface MoodBadgeProps {
  className?: string;
}

// Shows the emotion Fish Audio is currently performing, published via expressive mode
export function MoodBadge({ className }: MoodBadgeProps) {
  const { mood, expression } = useAgentExpression({ ttlTurns: 3 });
  const color = mood ? MOOD_COLORS[mood] : undefined;

  return (
    <AnimatePresence>
      {mood && (
        <motion.div
          key={mood}
          initial={{ opacity: 0, y: 6, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -6, scale: 0.95 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
          title={expression ?? undefined}
          className={cn(
            'pointer-events-none flex items-center gap-2 rounded-full border px-3 py-1.5',
            'bg-background/80 font-mono text-xs font-bold tracking-wider uppercase backdrop-blur',
            className
          )}
          style={{ borderColor: color, color }}
        >
          <span className="size-2 animate-pulse rounded-full" style={{ backgroundColor: color }} />
          {mood}
          <span className="text-muted-foreground font-normal tracking-normal normal-case">
            Fish Audio
          </span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
