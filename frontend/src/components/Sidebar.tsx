import { Plus, Search, Library, Settings } from 'lucide-react';
import React, { useEffect, useState } from 'react';

interface SidebarProps {
    onNewTask: () => void;
    onOpenConfig: () => void;
    history: any[];
    currentTaskId: string | null;
    onSelectTask: (taskId: string) => void;
}

export function Sidebar({ onNewTask, onOpenConfig, history, currentTaskId, onSelectTask }: SidebarProps) {
    return (
        <div className="side-panel">
            <div className="side-panel-header">
                {/* Placeholder for Logo if needed */}
            </div>

            <div className="sidebar-nav">
                <button className="sidebar-btn new-task-btn" onClick={onNewTask}>
                    <Plus size={20} />
                    Nouvelle tâche
                </button>
                <div className="nav-divider"></div>
                <button className="sidebar-btn" onClick={() => console.log('Search')}>
                    <Search size={20} />
                    Rechercher
                </button>
                <button className="sidebar-btn">
                    <Library size={20} />
                    Bibliothèque
                </button>
            </div>

            <div className="history-label">Récents</div>
            <div className="history-panel">
                <div className="task-list">
                    {history.map(task => (
                        <button
                            key={task.id}
                            className={`task-item ${currentTaskId === task.id ? 'active' : ''}`}
                            onClick={() => onSelectTask(task.id)}
                        >
                            <div className="task-title">{task.prompt}</div>
                        </button>
                    ))}
                </div>
            </div>

            <div className="set-config-panel">
                <button className="sidebar-result-btn" onClick={onOpenConfig} title="Configuration Settings">
                    <Settings size={20} />
                    Réglages
                </button>
            </div>
        </div>
    );
}
