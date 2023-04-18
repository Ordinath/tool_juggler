import React, { useState, useEffect } from 'react';

const BlinkingDots = ({ children, cycleTime = 333, maxDots = 3 }) => {
    const [dots, setDots] = useState('');

    useEffect(() => {
        const updateDots = () => {
            setDots((prevDots) => {
                if (prevDots.length === maxDots) {
                    return '';
                }
                return prevDots + '.';
            });
        };

        // Create a new interval for the dots
        const intervalId = setInterval(updateDots, cycleTime);

        // Clean up the interval on component unmount
        return () => {
            clearInterval(intervalId);
        };
    }, [cycleTime, maxDots]);

    const text = React.Children.toArray(children).join('');

    return <>{text + dots}</>;
};

export default BlinkingDots;
