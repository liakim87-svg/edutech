import React, { useState, useMemo } from 'react';
import { 
  LayoutDashboard, 
  ClipboardCheck, 
  AlertTriangle, 
  Search, 
  Save, 
  CheckCircle2, 
  Monitor, 
  Users,
  Settings
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

const App = () => {
  // Initial Data Setup
  const initialData = useMemo(() => {
    const data = [];
    for (let b = 1; b <= 3; b++) {
      for (let s = 1; s <= 20; s++) {
        const id = `1${b}${String(s).padStart(2, '0')}`;
        data.push({
          id: id,
          name: `Student ${id}`,
          class: `${b}nd Class`,
          status: 'Stored',
          detail: '',
          lastUpdated: new Date().toLocaleTimeString()
        });
      }
    }
    return data;
  }, []);

  const [chromebooks, setChromebooks] = useState(initialData);
  const [selectedClass, setSelectedClass] = useState('1nd Class');
  const [selectedStudent, setSelectedStudent] = useState(initialData[0].id);
  const [statusInput, setStatusInput] = useState('Stored');
  const [detailInput, setDetailInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showToast, setShowToast] = useState(false);

  // Statistics Calculation
  const stats = useMemo(() => {
    const total = chromebooks.length;
    const stored = chromebooks.filter(c => c.status === 'Stored').length;
    const rented = chromebooks.filter(c => c.status === 'Rented').length;
    const issue = chromebooks.filter(c => c.status === 'Missing' || c.status === 'Broken').length;
    
    const statusData = [
      { name: 'Stored', value: stored, color: '#10b981' },
      { name: 'Rented', value: rented, color: '#3b82f6' },
      { name: 'Missing', value: chromebooks.filter(c => c.status === 'Missing').length, color: '#ef4444' },
      { name: 'Broken', value: chromebooks.filter(c => c.status === 'Broken').length, color: '#f59e0b' },
    ];

    const classData = ['1nd Class', '2nd Class', '3nd Class'].map(cls => ({
      name: cls,
      rate: Math.round((chromebooks.filter(c => c.class === cls && c.status === 'Stored').length / 20) * 100)
    }));

    return { total, stored, rented, issue, statusData, classData };
  }, [chromebooks]);

  // Actions
  const handleUpdate = () => {
    setChromebooks(prev => prev.map(c => 
      c.id === selectedStudent 
        ? { ...c, status: statusInput, detail: detailInput, lastUpdated: new Date().toLocaleTimeString() }
        : c
    ));
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  const filteredList = chromebooks.filter(c => 
    c.id.includes(searchTerm) || c.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900">
      {/* Sidebar - Assistant Input Area */}
      <aside className="w-80 bg-white border-r border-slate-200 p-6 flex flex-col shadow-sm">
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-blue-600 p-2 rounded-lg text-white">
            <Monitor size={24} />
          </div>
          <h1 className="text-xl font-bold tracking-tight">Admin Menu</h1>
        </div>

        <div className="space-y-6 flex-1">
          <section>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">Class Selection</label>
            <select 
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              value={selectedClass}
              onChange={(e) => {
                const newClass = e.target.value;
                setSelectedClass(newClass);
                setSelectedStudent(chromebooks.find(c => c.class === newClass).id);
              }}
            >
              <option value="1nd Class">1st Grade - Class 1</option>
              <option value="2nd Class">1st Grade - Class 2</option>
              <option value="3nd Class">1st Grade - Class 3</option>
            </select>
          </section>

          <section>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">Student Name</label>
            <select 
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              value={selectedStudent}
              onChange={(e) => setSelectedStudent(e.target.value)}
            >
              {chromebooks.filter(c => c.class === selectedClass).map(c => (
                <option key={c.id} value={c.id}>{c.id} {c.name}</option>
              ))}
            </select>
          </section>

          <section>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">Device Status</label>
            <div className="grid grid-cols-2 gap-2">
              {['Stored', 'Rented', 'Missing', 'Broken'].map((s) => (
                <button
                  key={s}
                  onClick={() => setStatusInput(s)}
                  className={`py-2 px-3 rounded-lg text-sm font-medium transition-all border ${
                    statusInput === s 
                    ? 'bg-blue-600 border-blue-600 text-white shadow-md shadow-blue-100' 
                    : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </section>

          <section>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">Issue Details</label>
            <textarea 
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 h-24 resize-none outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              placeholder="Enter details if any..."
              value={detailInput}
              onChange={(e) => setDetailInput(e.target.value)}
            />
          </section>

          <button 
            onClick={handleUpdate}
            className="w-full bg-slate-900 text-white font-bold py-4 rounded-xl hover:bg-slate-800 transition-all flex items-center justify-center gap-2 shadow-lg shadow-slate-200 active:scale-95"
          >
            <Save size={18} />
            Update Status
          </button>
        </div>

        {showToast && (
          <div className="mt-4 bg-green-500 text-white p-3 rounded-lg flex items-center gap-2 animate-bounce">
            <CheckCircle2 size={18} />
            <span className="text-sm font-bold">Successfully Updated!</span>
          </div>
        )}
      </aside>

      {/* Main Content - Dashboard */}
      <main className="flex-1 overflow-y-auto p-10">
        <header className="flex justify-between items-end mb-10">
          <div>
            <div className="flex items-center gap-2 text-blue-600 font-bold mb-1">
              <LayoutDashboard size={18} />
              <span className="text-sm uppercase tracking-widest">Management Dashboard</span>
            </div>
            <h2 className="text-3xl font-extrabold text-slate-900">Chromebook Status</h2>
          </div>
          <div className="flex gap-4">
            <div className="bg-white p-3 px-5 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
              <div className="text-right">
                <p className="text-xs font-bold text-slate-400">Total Devices</p>
                <p className="text-xl font-black text-slate-900">{stats.total}</p>
              </div>
              <Monitor className="text-slate-300" size={32} />
            </div>
          </div>
        </header>

        {/* Metrics Cards */}
        <div className="grid grid-cols-3 gap-6 mb-10">
          <div className="bg-emerald-500 p-6 rounded-3xl text-white shadow-lg shadow-emerald-100 flex justify-between items-start">
            <div>
              <p className="font-bold opacity-80 mb-1">Stored Safely</p>
              <h3 className="text-4xl font-black">{stats.stored}</h3>
            </div>
            <div className="bg-white/20 p-2 rounded-xl">
              <CheckCircle2 size={24} />
            </div>
          </div>
          <div className="bg-blue-500 p-6 rounded-3xl text-white shadow-lg shadow-blue-100 flex justify-between items-start">
            <div>
              <p className="font-bold opacity-80 mb-1">Currently Rented</p>
              <h3 className="text-4xl font-black">{stats.rented}</h3>
            </div>
            <div className="bg-white/20 p-2 rounded-xl">
              <ClipboardCheck size={24} />
            </div>
          </div>
          <div className="bg-red-500 p-6 rounded-3xl text-white shadow-lg shadow-red-100 flex justify-between items-start">
            <div>
              <p className="font-bold opacity-80 mb-1">Issues Reported</p>
              <h3 className="text-4xl font-black">{stats.issue}</h3>
            </div>
            <div className="bg-white/20 p-2 rounded-xl">
              <AlertTriangle size={24} />
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-2 gap-8 mb-10">
          <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full" />
              Real-time Status Distribution
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.statusData}
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {stats.statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <div className="w-2 h-2 bg-indigo-500 rounded-full" />
              Return Rate by Class (%)
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.classData}>
                  <XAxis dataKey="name" axisLine={false} tickLine={false} />
                  <YAxis hide domain={[0, 100]} />
                  <Tooltip cursor={{fill: 'transparent'}} />
                  <Bar dataKey="rate" fill="#6366f1" radius={[10, 10, 10, 10]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Search and Table */}
        <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-50 flex justify-between items-center bg-slate-50/50">
            <div className="flex items-center gap-2">
              <Users size={20} className="text-slate-400" />
              <h3 className="font-bold text-slate-800">Complete Inventory List</h3>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input 
                type="text" 
                placeholder="Search student ID or name..."
                className="pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-400 w-64 transition-all"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="max-h-[500px] overflow-y-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50/80 sticky top-0 backdrop-blur-sm z-10">
                <tr>
                  <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase">ID</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Name</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Class</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Status</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Details</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase text-right">Last Update</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {filteredList.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="px-6 py-4 text-sm font-mono text-slate-500">{item.id}</td>
                    <td className="px-6 py-4 text-sm font-bold text-slate-800">{item.name}</td>
                    <td className="px-6 py-4 text-sm text-slate-600">{item.class}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-[11px] font-black uppercase tracking-widest ${
                        item.status === 'Stored' ? 'bg-emerald-100 text-emerald-700' :
                        item.status === 'Rented' ? 'bg-blue-100 text-blue-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-500 italic max-w-xs truncate">
                      {item.detail || '-'}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400 text-right font-medium">
                      {item.lastUpdated}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredList.length === 0 && (
              <div className="p-20 text-center text-slate-400 italic">
                No matching records found.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
