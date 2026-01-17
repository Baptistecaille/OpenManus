import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface ConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    config: any;
    onSave: (newConfig: any) => void;
}

export function ConfigModal({ isOpen, onClose, config, onSave }: ConfigModalProps) {
    const [formData, setFormData] = useState(config || {
        llm: { model: '', base_url: '', api_key: '' },
        server: { host: 'localhost', port: 5172 }
    });

    useEffect(() => {
        if (config) setFormData(config);
    }, [config]);

    const handleChange = (section: string, field: string, value: string) => {
        setFormData(prev => ({
            ...prev,
            [section]: {
                ...prev[section],
                [field]: value
            }
        }));
    }

    if (!isOpen) return null;

    return (
        <div className="config-modal active">
            <div className="config-modal-content">
                <div className="config-modal-header">
                    <h2>Configuration système</h2>
                    <button className="close-modal" onClick={onClose}><X size={20} /></button>
                </div>
                <div className="config-modal-body">
                    {/* Form fields mimicking the original HTML form */}
                    <div className="config-section">
                        <h3>LLM Configuration</h3>
                        <div className="form-group">
                            <label>Model Name</label>
                            <input
                                value={formData.llm?.model || ''}
                                onChange={e => handleChange('llm', 'model', e.target.value)}
                            />
                        </div>
                        <div className="form-group">
                            <label>Base URL</label>
                            <input
                                value={formData.llm?.base_url || ''}
                                onChange={e => handleChange('llm', 'base_url', e.target.value)}
                            />
                        </div>
                        <div className="form-group">
                            <label>API Key</label>
                            <input
                                type="password"
                                value={formData.llm?.api_key || ''}
                                onChange={e => handleChange('llm', 'api_key', e.target.value)}
                            />
                        </div>
                    </div>
                </div>
                <div className="config-modal-footer">
                    <button className="secondary-btn" onClick={onClose}>Annuler</button>
                    <button className="primary-btn" onClick={() => onSave(formData)}>Sauvegarder</button>
                </div>
            </div>
        </div>
    );
}
