import { useState, useEffect } from 'react';

export function useClientSideState(key, defaultValue) {
    const [value, setValue] = useState(() => {
        if (typeof window !== 'undefined') {
            const storedValue = window.localStorage.getItem(key);
            return storedValue ? JSON.parse(storedValue) : defaultValue;
        }
        return defaultValue;
    });

    useEffect(() => {
        if (typeof window !== 'undefined') {
            window.localStorage.setItem(key, JSON.stringify(value));
        }
    }, [key, value]);

    return [value, setValue];
}
