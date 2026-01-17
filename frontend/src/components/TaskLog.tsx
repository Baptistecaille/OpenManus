import React, { useEffect, useRef } from 'react';
import { Download, Play } from 'lucide-react';

interface Step {
    type: string;
    content: string;
    timestamp: string;
}

interface TaskLogProps {
    steps: Step[];
    isThinking: boolean;
}

export function TaskLog({ steps, isThinking }: TaskLogProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current) {
            // Auto scrollLogic
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [steps]);

    const renderFileInteraction = (content: string) => {
        const match = content.match(/Content successfully saved to (.+)/);
        if (!match) return null;

        const filePath = match[1].trim();
        const fileName = filePath.split('/').pop();
        // simplified logic for React
        return (
            <div className="file-interaction">
                <a href={`/download?file_path=${filePath}`} download={fileName} className="download-link">
                    <Download size={14} /> Télécharger {fileName}
                </a>
            </div>
        )
    }

    return (
        <div className="task-container" ref={containerRef} style={{ height: '100%', overflowY: 'auto' }}>
            <div className="step-container">
                {steps.map((step, index) => (
                    <div key={index} className={`step-item ${step.type} show`}>
                        <div className="log-line">
                            <span className="log-prefix">[{step.timestamp}] {step.type.toUpperCase()}:</span>
                            <pre>{step.content}</pre>
                            {step.type === 'act' && renderFileInteraction(step.content)}
                        </div>
                    </div>
                ))}
                {isThinking && <div className="loading">Thinking...</div>}
            </div>
        </div>
    );
}
