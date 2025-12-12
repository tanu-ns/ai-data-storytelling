export default function InsightList({ insights }: { insights: any[] }) {
    if (!insights || insights.length === 0) return <p className="text-gray-500">No automated insights yet.</p>;

    return (
        <div className="space-y-4">
            {insights.map((insight, idx) => (
                <div key={idx} className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow border-l-4 border-blue-500">
                    <div className="flex justify-between items-start">
                        <h3 className="font-bold text-lg">{insight.title}</h3>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            Conf: {(insight.confidence * 100).toFixed(0)}%
                        </span>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 mt-2">{insight.description}</p>

                    <div className="mt-4 bg-gray-100 dark:bg-gray-900 p-2 rounded text-xs font-mono overflow-auto">
                        <p className="text-gray-500 mb-1">Verification:</p>
                        <code>{insight.verification_code}</code>
                    </div>
                </div>
            ))}
        </div>
    );
}
