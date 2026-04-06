import { getPages, getPosts, getCategories } from '@/lib/wordpress';

export const dynamic = 'force-dynamic';

export default async function Home() {
  const [pages, posts, categories] = await Promise.all([
    getPages({ _fields: 'id,title,slug,status,link,modified' }),
    getPosts({ _fields: 'id,title,slug,status,link,modified' }),
    getCategories(),
  ]);

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50">
      <header className="bg-[#253F55] text-white py-6 px-8">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">ברנדיני | לוח בקרה</h1>
            <p className="text-blue-200 text-sm mt-1">מחובר ל-brndini.co.il</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1.5 bg-green-500/20 text-green-300 px-3 py-1 rounded-full text-sm">
              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
              מחובר
            </span>
            <a
              href="https://brndini.co.il/wp-admin"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-sm transition-colors"
            >
              פאנל וורדפרס
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto py-8 px-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <p className="text-gray-500 text-sm">דפים</p>
            <p className="text-3xl font-bold text-[#253F55] mt-1">{pages.length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <p className="text-gray-500 text-sm">פוסטים</p>
            <p className="text-3xl font-bold text-[#253F55] mt-1">{posts.length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <p className="text-gray-500 text-sm">קטגוריות</p>
            <p className="text-3xl font-bold text-[#253F55] mt-1">{categories.length}</p>
          </div>
        </div>

        {/* Posts */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 mb-8">
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-xl font-bold text-[#253F55]">פוסטים אחרונים</h2>
          </div>
          <div className="divide-y divide-gray-50">
            {posts.map((post) => (
              <div key={post.id} className="p-4 px-6 hover:bg-gray-50 transition-colors flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900" dangerouslySetInnerHTML={{ __html: post.title.rendered }} />
                  <p className="text-sm text-gray-400 mt-0.5">/{post.slug}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${post.status === 'publish' ? 'bg-green-50 text-green-600' : 'bg-yellow-50 text-yellow-600'}`}>
                    {post.status === 'publish' ? 'מפורסם' : 'טיוטה'}
                  </span>
                  <a href={post.link} target="_blank" rel="noopener noreferrer" className="text-[#6EC1E4] hover:text-[#253F55] text-sm">
                    צפה
                  </a>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Pages */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-xl font-bold text-[#253F55]">דפים</h2>
          </div>
          <div className="divide-y divide-gray-50">
            {pages.map((page) => (
              <div key={page.id} className="p-4 px-6 hover:bg-gray-50 transition-colors flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900" dangerouslySetInnerHTML={{ __html: page.title.rendered }} />
                  <p className="text-sm text-gray-400 mt-0.5">/{page.slug}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${page.status === 'publish' ? 'bg-green-50 text-green-600' : 'bg-yellow-50 text-yellow-600'}`}>
                    {page.status === 'publish' ? 'מפורסם' : 'טיוטה'}
                  </span>
                  <a href={page.link} target="_blank" rel="noopener noreferrer" className="text-[#6EC1E4] hover:text-[#253F55] text-sm">
                    צפה
                  </a>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
