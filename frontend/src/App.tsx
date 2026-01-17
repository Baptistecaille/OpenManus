import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Sidebar } from './components/Sidebar';
import { InputArea } from './components/InputArea';
import { TaskLog } from './components/TaskLog';
import { ConfigModal } from './components/ConfigModal';
import { Play } from 'lucide-react';

// Types
interface Task {
    id: string;
    prompt: string;
    status: string;
    created_at: string;
}

function App() {
    const [history, setHistory] = useState<Task[]>([]);
    const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
    const [steps, setSteps] = useState<any[]>([]);
    const [isThinking, setIsThinking] = useState(false);
    const [configOpen, setConfigOpen] = useState(false);
    const [config, setConfig] = useState(null);
    const [disabled, setDisabled] = useState(false); // Config missing

    const eventSourceRef = useRef<EventSource | null>(null);

    // Load initial data
    useEffect(() => {
        checkConfig();
        loadHistory();
    }, []);

    const checkConfig = async () => {
        try {
            const res = await axios.get('/config/status');
            if (res.data.status === 'missing') {
                setDisabled(true);
                setConfigOpen(true);
            } else {
                setDisabled(false);
            }
        } catch (e) {
            console.error("Config check failed", e);
        }
    };

    const loadHistory = async () => {
        try {
            const res = await axios.get('/tasks');
            setHistory(res.data);
        } catch (e) {
            console.error("Load history failed", e);
        }
    }

    const handleNewTask = () => {
        setCurrentTaskId(null);
        setSteps([]);
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
    };

    const handleCreateTask = async (prompt: string) => {
        try {
            setIsThinking(true);
            const res = await axios.post('/tasks', { prompt });
            const taskId = res.data.task_id;
            setCurrentTaskId(taskId);

            // Refresh history
            loadHistory();

            // Start SSE
            connectSSE(taskId);
        } catch (e) {
            console.error("Create task failed", e);
            setIsThinking(false);
        }
    };

    const connectSSE = (taskId: string) => {
        if (eventSourceRef.current) eventSourceRef.current.close();

        const eventSource = new EventSource(`/tasks/${taskId}/events`);
        eventSourceRef.current = eventSource;

        const handleEvent = (event: MessageEvent, type: string) => {
            try {
                const data = JSON.parse(event.data);
                setSteps(prev => [...prev, { type, content: data.result, timestamp: new Date().toLocaleTimeString() }]);
                if (type === 'complete' || type === 'error') {
                    setIsThinking(false);
                    eventSource.close();
                }
            } catch (e) {
                console.error("Parse event error", e);
            }
        };

        ['think', 'tool', 'act', 'log', 'run', 'message', 'complete', 'error'].forEach(type => {
            eventSource.addEventListener(type, (e: any) => handleEvent(e, type));
        });
    };

    const handleSuggestion = (text: string) => {
        handleCreateTask(text);
    };

    const handleSaveConfig = async (newConfig: any) => {
        try {
            await axios.post('/config/save', newConfig);
            setConfigOpen(false);
            setDisabled(false);
            alert("Configuration saved!");
        } catch (e) {
            alert("Failed to save config");
        }
    };

    return (
        <div className="container">
            <Sidebar
                onNewTask={handleNewTask}
                onOpenConfig={() => setConfigOpen(true)}
                history={history}
                currentTaskId={currentTaskId}
                onSelectTask={(id) => setCurrentTaskId(id)} // Logic to load old task steps not fully implemented yet
            />

            <div className="main-panel">
                {!currentTaskId ? (
                    <div className="welcome-message">
                        <h1>Que souhaitez-vous accomplir ?</h1>
                        <div className="suggestions">
                            {['Créer des diapositives', 'Créer un site web', 'Développer une application', 'Analyser des données'].map(t => (
                                <button key={t} className="suggestion-chip" onClick={() => handleSuggestion(t)}>
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <TaskLog steps={steps} isThinking={isThinking} />
                )}

                <InputArea onSend={handleCreateTask} disabled={disabled || isThinking} />
            </div>

            <ConfigModal
                isOpen={configOpen}
                onClose={() => setConfigOpen(false)}
                config={config}
                onSave={handleSaveConfig}
            />
        </div>
    )
}

export default App
