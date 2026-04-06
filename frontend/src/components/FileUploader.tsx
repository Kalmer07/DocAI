import React, { useState, useRef } from 'react';
import { useAppStore } from '../hooks/useAppStore';
import { uploadFiles } from '../services/documents';

interface FileUploaderProps {
  onUploadComplete?: () => void;
}

export const FileUploader: React.FC<FileUploaderProps> = ({ onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const addFiles = useAppStore((state) => state.addFiles);

  const handleFiles = async (filesList: File[]) => {
    if (filesList.length === 0) return;
    
    setIsUploading(true);
    try {
      const uploaded = await uploadFiles(filesList);
      addFiles(uploaded);
      onUploadComplete?.();
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Ошибка загрузки файлов');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(Array.from(e.dataTransfer.files));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  return (
    <div className="file-uploader p-4">
      <div
        className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragging 
            ? 'border-indigo-500 bg-indigo-500/10' 
            : 'border-slate-600 hover:border-indigo-400 hover:bg-slate-700/50'}
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.md,.csv,.pdf,.docx,.doc"
          className="hidden"
          onChange={handleFileInput}
        />
        
        {isUploading ? (
          <div className="flex flex-col items-center gap-3">
            <div className="spinner"></div>
            <p className="text-slate-400">Загрузка файлов...</p>
          </div>
        ) : (
          <>
            <svg
              className="w-12 h-12 mx-auto mb-4 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            
            <p className="text-lg font-medium text-slate-200">
              Перетащите файлы сюда или кликните для выбора
            </p>
            <p className="text-sm text-slate-400 mt-2">
              Поддерживаются: TXT, MD, CSV, PDF, DOCX (3-15 файлов)
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default FileUploader;
