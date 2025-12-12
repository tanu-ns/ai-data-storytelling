"use client";

import { useState, useEffect } from "react";
import DatasetProfile from "@/components/DatasetProfile";
import InsightList from "@/components/InsightList";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import ChatInterface from "@/components/ChatInterface";

export default function Dashboard() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [writingStory, setWritingStory] = useState(false);
    const [message, setMessage] = useState("");
    const [datasets, setDatasets] = useState<any[]>([]);
    const [selectedDataset, setSelectedDataset] = useState<any>(null);
    const [activeTab, setActiveTab] = useState("analysis"); // analysis | chat

    const fetchDatasets = async () => {
        const email = localStorage.getItem("userEmail");
        if (!email) return;

        try {
            const res = await fetch("http://localhost:8000/datasets/", {
                headers: { "X-User-Email": email }
            });
            if (res.ok) {
                setDatasets(await res.json());
            }
        } catch (e) {
            console.error(e);
        }
    };

    const fetchDatasetDetails = async (id: string) => {
        const email = localStorage.getItem("userEmail");
        try {
            const res = await fetch(`http://localhost:8000/datasets/${id}`, {
                headers: { "X-User-Email": email || "" }
            });
            if (res.ok) {
                setSelectedDataset(await res.json());
            }
        } catch (e) {
            console.error(e);
        }
    };

    const generateInsights = async () => {
        if (!selectedDataset) return;
        setGenerating(true);
        const email = localStorage.getItem("userEmail");

        try {
            const res = await fetch(`http://localhost:8000/datasets/${selectedDataset.id}/insights`, {
                method: "POST",
                headers: { "X-User-Email": email || "" }
            });

            if (res.ok) {
                const insights = await res.json();
                setSelectedDataset({ ...selectedDataset, insights });
            }
        } catch (e) {
            console.error(e);
        } finally {
            setGenerating(false);
        }
    };

    const generateStory = async () => {
        if (!selectedDataset) return;
        setWritingStory(true);
        const email = localStorage.getItem("userEmail");

        try {
            const res = await fetch(`http://localhost:8000/datasets/${selectedDataset.id}/story`, {
                method: "POST",
                headers: { "X-User-Email": email || "" }
            });

            if (res.ok) {
                const data = await res.json();
                setSelectedDataset({ ...selectedDataset, story: data.story });
            }
        } catch (e) {
            console.error(e);
        } finally {
            setWritingStory(false);
        }
    };

    const downloadStory = () => {
        if (!selectedDataset?.story) return;
        const blob = new Blob([selectedDataset.story], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedDataset.name}_story.md`;
        a.click();
    };

    useEffect(() => {
        fetchDatasets();
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        const email = localStorage.getItem("userEmail");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("http://localhost:8000/datasets/upload", {
                method: "POST",
                headers: {
                    "X-User-Email": email || "",
                },
                body: formData,
            });

            if (res.ok) {
                setMessage("Upload successful! Analyzing...");
                setFile(null);
                await fetchDatasets();
                const newDs = await res.json();
                fetchDatasetDetails(newDs.id);
            } else {
                const err = await res.json();
                setMessage(`Error: ${err.detail}`);
            }
        } catch (error) {
            setMessage("Upload failed due to network error.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="min-h-screen p-8 bg-gray-100 text-gray-900 dark:bg-gray-900 dark:text-white flex flex-col lg:flex-row gap-8">

            {/* Sidebar / Upload Section */}
            <div className="w-full lg:w-1/3 space-y-8">
                <h1 className="text-3xl font-bold">Dashboard</h1>

                <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                    <h2 className="text-xl font-semibold mb-4">Upload Dataset (CSV)</h2>
                    <div className="space-y-4">
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileChange}
                            className="block w-full text-sm text-gray-500
                                file:mr-4 file:py-2 file:px-4
                                file:rounded-full file:border-0
                                file:text-sm file:font-semibold
                                file:bg-blue-50 file:text-blue-700
                                hover:file:bg-blue-100"
                        />
                        <button
                            onClick={handleUpload}
                            disabled={!file || uploading}
                            className={`w-full py-2 px-4 rounded-md font-bold text-white 
                                ${!file || uploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
                        >
                            {uploading ? "Uploading & Analyzing..." : "Upload"}
                        </button>
                        {message && <p className="mt-2 text-sm">{message}</p>}
                    </div>
                </div>

                <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                    <h2 className="text-xl font-semibold mb-4">Your Datasets</h2>
                    <ul className="space-y-2">
                        {datasets.map(ds => (
                            <li key={ds.id}>
                                <button
                                    onClick={() => fetchDatasetDetails(ds.id)}
                                    className={`w-full text-left px-4 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 ${selectedDataset?.id === ds.id ? 'bg-blue-100 dark:bg-blue-900' : ''}`}
                                >
                                    {ds.name} <span className="text-xs opacity-50 block">{new Date(ds.created_at).toLocaleString()}</span>
                                </button>
                            </li>
                        ))}
                        {datasets.length === 0 && <p className="text-sm opacity-50">No datasets yet.</p>}
                    </ul>
                </div>
            </div>

            {/* Main Content */}
            <div className="w-full lg:w-2/3 space-y-8">
                {selectedDataset ? (
                    <>
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-2xl font-bold">{selectedDataset.name}</h2>
                            <div className="flex space-x-2">
                                <button
                                    onClick={() => setActiveTab('analysis')}
                                    className={`px-4 py-2 rounded font-bold ${activeTab === 'analysis' ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}
                                >
                                    Analysis
                                </button>
                                <button
                                    onClick={() => setActiveTab('chat')}
                                    className={`px-4 py-2 rounded font-bold ${activeTab === 'chat' ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}
                                >
                                    Chat
                                </button>
                            </div>
                        </div>

                        {activeTab === 'analysis' && (
                            <>
                                <div className="flex justify-end space-x-2 mb-4">
                                    <button
                                        onClick={generateInsights}
                                        disabled={generating}
                                        className={`px-4 py-2 rounded font-bold text-white ${generating ? 'bg-purple-400' : 'bg-purple-600 hover:bg-purple-700'}`}
                                    >
                                        {generating ? "Analyzing..." : "✨ Generate Insights"}
                                    </button>
                                    {selectedDataset.insights && (
                                        <button
                                            onClick={generateStory}
                                            disabled={writingStory}
                                            className={`px-4 py-2 rounded font-bold text-white ${writingStory ? 'bg-green-400' : 'bg-green-600 hover:bg-green-700'}`}
                                        >
                                            {writingStory ? "Writing..." : "📝 Write Story"}
                                        </button>
                                    )}
                                </div>

                                <DatasetProfile data={selectedDataset} />

                                {/* Insights Section */}
                                {selectedDataset.insights && (
                                    <div id="insights">
                                        <h2 className="text-2xl font-bold mb-4">AI Business Insights</h2>
                                        <InsightList insights={selectedDataset.insights} />
                                    </div>
                                )}

                                {/* Story Section */}
                                {selectedDataset.story && (
                                    <div id="story" className="mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg border-t-4 border-green-500">
                                        <div className="flex justify-between items-center mb-4">
                                            <h2 className="text-2xl font-bold">Executive Report</h2>
                                            <button onClick={downloadStory} className="text-sm text-blue-500 hover:underline">Download Markdown</button>
                                        </div>
                                        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded">
                                            <MarkdownRenderer content={selectedDataset.story} />
                                        </div>
                                    </div>
                                )}
                            </>
                        )}

                        {activeTab === 'chat' && (
                            <ChatInterface datasetId={selectedDataset.id} />
                        )}
                    </>
                ) : (
                    <div className="flex items-center justify-center h-full opacity-50">
                        <p>Select a dataset to view insights</p>
                    </div>
                )}
            </div>

        </div>
    );
}
