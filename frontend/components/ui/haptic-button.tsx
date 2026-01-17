import React from 'react';
import { Button, buttonVariants } from '@/components/ui/button';
import { VariantProps } from 'class-variance-authority';
import { useHapticClick } from '@/hooks/use-haptics';
import { HapticStyle } from '@/lib/haptics';

interface HapticButtonProps extends React.ComponentProps<'button'>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean;
    hapticStyle?: HapticStyle;
    onHapticClick?: () => void;
}

/**
 * Button component with built-in haptic feedback
 * Automatically triggers haptic feedback when clicked
 */
export function HapticButton({
    hapticStyle = 'medium',
    onHapticClick,
    onClick,
    children,
    ...props
}: HapticButtonProps) {
    const handleClick = useHapticClick(() => {
        onHapticClick?.();
        if (onClick) {
            onClick(undefined as any);
        }
    }, hapticStyle);

    return (
        <Button onClick={handleClick} {...props}>
            {children}
        </Button>
    );
}
