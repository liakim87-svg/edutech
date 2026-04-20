import React, { useState, useMemo, useEffect } from 'react';
import { 
  LayoutDashboard, 
  ClipboardCheck, 
  AlertTriangle, 
  Search, 
  Save, 
  CheckCircle2, 
  Monitor, 
  Users,
  Clock,
  ChevronRight
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

const App = () => {
  // 초기 데이터 생성
  const initialData = useMemo(() => {
    const data = [];
    const classes = ['1반', '2반', '3반'];
    classes.forEach((cls) => {
      for (let s = 1; s <= 20; s++) {
        const id = `${cls === '1반' ? '1' : cls === '2반' ? '2' : '3'}${String(s).padStart(2, '0')}`;
        data.push({
          id: id,
          name: `학생 ${id}`,
          class: cls,
          status: '정상 반납',
          detail: '',
          lastUpdated: new Date().toLocaleTimeString('ko-KR')
        });
      }
    });
    return data;
  }, []);

  const [chromebooks, setChromebooks] = useState(initialData);
  const [selectedClass, setSelectedClass] = useState('1반');
  const [selectedStudent, setSelectedStudent] = useState(initialData[0].id);
  const [statusInput, setStatusInput] = useState('정상 반납');
  const [detailInput, setDetailInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showToast, setShowToast] = useState(false);

  // 통계 계산
  const stats = useMemo(() => {
    const total = chromebooks.length;
    const stored = chromebooks.filter(c => c.status === '정상 반납').length;
    const rented = chromebooks.filter(c => c.status === '대여 중').length;
    const issue = chromebooks.filter(c => c.status === '분실' || c.status === '파손').length;
    
    const statusData = [
      { name: '정상 반납', value: stored, color: '#10b981' },
      { name: '대여 중', value: rented, color: '#3b82f6' },
      { name: '분실', value: chromebooks.filter(c => c.status === '분실').length, color: '#ef4444' },
      { name: '파손', value: chromebooks.filter(c => c.status === '파손').length, color: '#f59e0b' },
    ];

    const classData = ['1반', '2반', '3반'].map(cls => ({
      name: cls,
      rate: Math.round((chromebooks.filter(c => c.class === cls && c.status === '정상 반납').length / 20) * 100)
    }));

    return { total, stored, rented, issue, statusData, classData };
  }, [chromebooks]);

  // 상태 업데이트 로직
  const handleUpdate = () => {
    setChromebooks(prev => prev.map(c => 
      c.id === selectedStudent 
        ? { ...c, status: statusInput, detail: detailInput, lastUpdated: new Date().toLocaleTimeString('ko-KR') }
        : c
    ));
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  const filteredList = chromebooks.filter(c => 
    c.id.includes(searchTerm) || c.name.includes(searchTerm)
  );

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      {/* 사이드바 - 관리 메뉴 */}
      <aside className="w-80 bg-white border-r border-slate-200 p-6 flex flex-col shadow-sm z-20">
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-indigo-600 p-2 rounded-xl text-white shadow-lg shadow-indigo-100">
            <Monitor size={24} />
          </div>
          <h1 className="text-xl font-bold tracking-tight">크롬북 관리 시스템</h1>
        </div>

        <div className="space-y-6 flex-1 overflow-y-auto pr-1">
          <section>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">학급 선택</label>
            <select 
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500 transition-all cursor-pointer"
              value={selectedClass}
              onChange={(e) => {
                const newClass = e.target.value;
                setSelectedClass(newClass);
                const firstStudent = chromebooks.find(c => c.class === newClass);
                if(firstStudent) setSelectedStudent(firstStudent.id);
              }}
            >
              <option value="1반">1학년 1반</option>
              <option value="1학년 2반">1학년 2반</option>
              <option value="1학년 3반">1학년 3반</option>
            </select>
          </section>

          <section>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">학생 선택</label>
            <select 
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500 transition-all cursor-pointer"
              value={selectedStudent}
              onChange={(e) => setSelectedStudent(e.target.value)}
            >
              {chromebooks.filter(c => c.class === selectedClass).map(c => (
                <option key={c.id} value={c.id}>{c.id}번 {c.name}</option>
              ))}
            </select>
          </section>

          <section>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">상태 설정</label>
            <div className="grid grid-cols-2 gap-2">
              {['정상 반납', '대여 중', '분실', '파손'].map((s) => (
                <button
                  key={s}
                  onClick={() => setStatusInput(s)}
                  className={`py-2.5 px-3 rounded-lg text-xs font-bold transition-all border ${
                    statusInput === s 
                    ? 'bg-indigo-600 border-indigo-600 text-white shadow-md shadow-indigo-100' 
                    : 'bg-white border-slate-200 text-slate-600 hover:border-indigo-300'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </section>

          <section>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">특이 사항</label>
            <textarea 
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 h-24 resize-none outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm"
              placeholder="파손 부위나 대여 사유 등을 적어주세요."
              value={detailInput}
              onChange={(e) => setDetailInput(e.target.value)}
            />
          </section>

          <button 
            onClick={handleUpdate}
            className="w-full bg-slate-900 text-white font-bold py-4 rounded-xl hover:bg-slate-800 transition-all flex items-center justify-center gap-2 shadow-lg shadow-slate-200 active:scale-95"
          >
            <Save size={18} />
            상태 업데이트
          </button>
        </div>

        {showToast && (
          <div className="mt-4 bg-emerald-500 text-white p-3 rounded-xl flex items-center gap-2 animate-bounce justify-center">
            <CheckCircle2 size={18} />
            <span className="text-sm font-bold">저장되었습니다!</span>
          </div>
        )}
      </aside>

      {/* 메인 대시보드 */}
      <main className="flex-1 overflow-y-auto p-8 lg:p-12">
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10">
          <div>
            <div className="flex items-center gap-2 text-indigo-600 font-bold mb-1">
              <LayoutDashboard size={18} />
              <span className="text-xs uppercase tracking-[0.2em]">Live Status Dashboard</span>
            </div>
            <h2 className="text-3xl font-black text-slate-900 tracking-tight">기기 현황판</h2>
          </div>
          <div className="flex gap-4">
            <div className="bg-white p-4 px-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
              <div className="text-right">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Total Assets</p>
                <p className="text-2xl font-black text-slate-900 leading-none mt-1">{stats.total}</p>
              </div>
              <div className="bg-slate-50 p-2 rounded-lg text-slate-300">
                <Monitor size={24} />
              </div>
            </div>
          </div>
        </header>

        {/* 핵심 지표 */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
          <div className="bg-emerald-500 p-6 rounded-[2rem] text-white shadow-xl shadow-emerald-100 flex justify-between items-start">
            <div>
              <p className="font-bold text-emerald-100 text-sm mb-1">정상 반납</p>
              <h3 className="text-4xl font-black leading-none">{stats.stored}</h3>
            </div>
            <div className="bg-white/20 p-2 rounded-xl">
              <CheckCircle2 size={24} />
            </div>
          </div>
          <div className="bg-blue-500 p-6 rounded-[2rem] text-white shadow-xl shadow-blue-100 flex justify-between items-start">
            <div>
              <p className="font-bold text-blue-100 text-sm mb-1">대여 중</p>
              <h3 className="text-4xl font-black leading-none">{stats.rented}</h3>
            </div>
            <div className="bg-white/20 p-2 rounded-xl">
              <Clock size={24} />
            </div>
          </div>
          <div className="bg-orange-500 p-6 rounded-[2rem] text-white shadow-xl shadow-orange-100 flex justify-between items-start">
            <div>
              <p className="font-bold text-orange-100 text-sm mb-1">점검 필요</p>
              <h3 className="text-4xl font-black leading-none">{stats.issue}</h3>
            </div>
            <div className="bg-white/20 p-2 rounded-xl">
              <AlertTriangle size={24} />
            </div>
          </div>
        </div>

        {/* 차트 영역 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
          <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm relative overflow-hidden group">
            <h3 className="font-bold text-slate-800 mb-8 flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full" />
              전체 기기 상태 분포
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.statusData}
                    innerRadius={65}
                    outerRadius={85}
                    paddingAngle={8}
                    dataKey="value"
                    animationBegin={0}
                    animationDuration={1500}
                  >
                    {stats.statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}}
                  />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-8 flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
              학급별 반납률 (%)
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.classData}>
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 12, fontWeight: 700}} />
                  <YAxis hide domain={[0, 100]} />
                  <Tooltip 
                    cursor={{fill: '#f8fafc'}}
                    contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}}
                  />
                  <Bar dataKey="rate" fill="#6366f1" radius={[8, 8, 8, 8]} barSize={45} animationDuration={2000} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* 인벤토리 목록 */}
        <div className="bg-white rounded-[2rem] border border-slate-100 shadow-sm overflow-hidden">
          <div className="p-8 flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-50/30">
            <div className="flex items-center gap-3">
              <div className="bg-white p-2 rounded-lg shadow-sm">
                <Users size={18} className="text-indigo-600" />
              </div>
              <h3 className="font-bold text-slate-800 text-lg">기기 상세 리스트</h3>
            </div>
            <div className="relative w-full sm:w-auto">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input 
                type="text" 
                placeholder="관리 번호 또는 이름 검색..."
                className="pl-12 pr-6 py-3 bg-white border border-slate-200 rounded-2xl text-sm outline-none focus:ring-2 focus:ring-indigo-500 w-full sm:w-80 transition-all shadow-sm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-100">
                  <th className="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">관리번호</th>
                  <th className="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">학생성명</th>
                  <th className="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">상태</th>
                  <th className="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">특이사항</th>
                  <th className="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">최근 업데이트</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {filteredList.map((item) => (
                  <tr key={item.id} className="hover:bg-indigo-50/30 transition-colors group">
                    <td className="px-8 py-5 text-sm font-black text-indigo-600">{item.id}</td>
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-700">{item.name}</span>
                        <span className="text-[10px] bg-slate-100 px-2 py-0.5 rounded text-slate-500 font-bold">{item.class}</span>
                      </div>
                    </td>
                    <td className="px-8 py-5">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black tracking-tighter ${
                        item.status === '정상 반납' ? 'bg-emerald-100 text-emerald-700' :
                        item.status === '대여 중' ? 'bg-blue-100 text-blue-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${
                          item.status === '정상 반납' ? 'bg-emerald-500' :
                          item.status === '대여 중' ? 'bg-blue-500' : 'bg-red-500'
                        }`} />
                        {item.status}
                      </span>
                    </td>
                    <td className="px-8 py-5 text-sm text-slate-500 italic max-w-xs truncate">
                      {item.detail || '-'}
                    </td>
                    <td className="px-8 py-5 text-xs text-slate-400 text-right font-medium">
                      {item.lastUpdated}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredList.length === 0 && (
              <div className="p-20 text-center flex flex-col items-center gap-3">
                <div className="bg-slate-50 p-4 rounded-full text-slate-300">
                  <Search size={32} />
                </div>
                <p className="text-slate-400 font-bold italic">검색 결과가 없습니다.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
