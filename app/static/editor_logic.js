// --- /editor_logic.js ---
document.addEventListener('DOMContentLoaded', () => {
    // ==========================================================================
    // 1. Inicialización y Autenticación
    // ==========================================================================
    const token = localStorage.getItem('docuhub_token');
    if (!token) { window.location.href = '/login'; } // Asumiendo que login.html está en la raíz o accesible como /login
    const authHeaders = { 'Authorization': `Bearer ${token}` };

    // ==========================================================================
    // 2. Lógica del Interruptor de Tema (Theme Switcher)
    // ==========================================================================
    const themeSwitcher = document.getElementById('theme-switcher');
    const htmlEl = document.documentElement;
    const applyTheme = (theme) => {
        htmlEl.setAttribute('data-theme', theme);
        themeSwitcher.textContent = theme === 'dark' ? '🌙' : '☀️';
        localStorage.setItem('docuhub_theme', theme);
    };
    themeSwitcher.addEventListener('click', () => {
        const currentTheme = htmlEl.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
    });
    const savedTheme = localStorage.getItem('docuhub_theme') || 'light';
    applyTheme(savedTheme);

    // ==========================================================================
    // 3. Referencias al DOM y Lógica de la Aplicación
    // ==========================================================================
    const fileTreeEl = document.getElementById('file-tree');
    const previewEl = document.getElementById('preview');
    const saveBtn = document.getElementById('save-btn');
    const publishBtn = document.getElementById('publish-btn');
    const statusEl = document.getElementById('status-message');
    const editorAreaWrapper = document.getElementById('editor-area-wrapper');

    let currentFilePath = null;
    let easyMDE;

    function renderTree(nodes, container) {
        const ul = document.createElement('ul');
        nodes.forEach(node => {
            const li = document.createElement('li');
            if (node.type === 'directory') {
                li.innerHTML = `<span class="directory">📁 ${node.name.replace(/_/g, ' ')}</span>`;
                if (node.children && node.children.length > 0) {
                    renderTree(node.children, li);
                }
            } else {
                li.innerHTML = `<span class="file" data-path="${node.path}">📄 ${node.name}</span>`;
            }
            ul.appendChild(li);
        });
        container.appendChild(ul);
    }

    async function loadFileTree() {
        try {
            const response = await fetch('/api/v1/documents/tree', { headers: authHeaders });
            if (!response.ok) {
                if (response.status === 401) window.location.href = '/login';
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const treeData = await response.json();
            fileTreeEl.innerHTML = '';
            renderTree(treeData, fileTreeEl);
        } catch (error) {
            console.error("Error loading file tree:", error);
            fileTreeEl.innerHTML = `<p style="color: red; padding: 1rem;">Error al cargar árbol de archivos.</p>`;
        }
    }

    async function loadFileContent(path) {
        currentFilePath = path;
        previewEl.innerHTML = '<p style="color: var(--text-muted); text-align: center; margin-top: 50px;">Cargando contenido...</p>';
        saveBtn.disabled = true; // Deshabilitar mientras carga
        try {
            const response = await fetch(`/api/v1/documents/content/${path}`, { headers: authHeaders });
            if (!response.ok) {
                if (response.status === 401) window.location.href = '/login';
                previewEl.innerHTML = '<p style="color: red; text-align: center; margin-top: 50px;">Error al cargar contenido del archivo.</p>';
                if (easyMDE) easyMDE.value("");
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (easyMDE) {
                easyMDE.value(data.content);
                // La función previewRender de EasyMDE o el observer se encargarán de actualizar el previewEl
                if (editorAreaWrapper.classList.contains('side-by-side-active')) {
                     previewEl.innerHTML = marked.parse(data.content); // Forzar actualización si ya está side-by-side
                }
            }
            saveBtn.disabled = false;
        } catch (error) {
            console.error("Error loading file content:", error);
            // El mensaje de error ya está en previewEl o se manejó la redirección
        }
    }

    // updatePreview no es necesaria como función separada si el previewRender y el observer manejan la actualización.
    // function updatePreview(value) { ... }

    saveBtn.addEventListener('click', async () => {
        if (!currentFilePath || !easyMDE) return;
        statusEl.textContent = 'Guardando...';
        saveBtn.disabled = true;
        try {
            const response = await fetch(`/api/v1/documents/content/${currentFilePath}`, {
                method: 'POST',
                headers: { ...authHeaders, 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: easyMDE.value() })
            });
            if (!response.ok) {
                 if (response.status === 401) window.location.href = '/login';
                 throw new Error(`HTTP error! status: ${response.status}`);
            }
            statusEl.textContent = '¡Guardado!';
        } catch (error) {
            console.error("Error saving file:", error);
            statusEl.textContent = 'Error al guardar.';
        } finally {
            saveBtn.disabled = false;
            setTimeout(() => statusEl.textContent = '', 3000);
        }
    });

    publishBtn.addEventListener('click', async () => {
        statusEl.textContent = 'Publicando...';
        publishBtn.disabled = true;
        try {
            const response = await fetch('/api/v1/documents/publish', {
                method: 'POST',
                headers: authHeaders
            });
            if (!response.ok) {
                if (response.status === 401) window.location.href = '/login';
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            statusEl.textContent = '¡Sitio publicado!';
        } catch (error) {
            console.error("Error publishing site:", error);
            statusEl.textContent = 'Error al publicar.';
        } finally {
            publishBtn.disabled = false;
            setTimeout(() => statusEl.textContent = '', 3000);
        }
    });

    fileTreeEl.addEventListener('click', (e) => {
        if (e.target && e.target.classList.contains('file')) {
            document.querySelectorAll('.file.active').forEach(el => el.classList.remove('active'));
            e.target.classList.add('active');
            loadFileContent(e.target.dataset.path);
        }
    });

    easyMDE = new EasyMDE({
        element: document.getElementById('markdown-editor'),
        spellChecker: false,
        status: ["lines", "words", "cursor"],
        toolbarTips: true,
        indentWithTabs: false,
        tabSize: 4,
        previewRender: function(plainText, preview) { // 'preview' es el elemento DOM del panel de preview de EasyMDE
            // Esta función se llama para renderizar en el panel de preview de EasyMDE
            // cuando está en modo side-by-side.
            // Actualizamos nuestro propio panel de preview.
            const currentPreviewHTML = marked.parse(plainText);
            document.getElementById('preview').innerHTML = currentPreviewHTML;
            return currentPreviewHTML; // Devolver el HTML parseado para que EasyMDE también lo use si lo necesita.
        },
    });

    easyMDE.codemirror.on("change", () => {
        if (currentFilePath) {
            saveBtn.disabled = false;
        }
    });

    const easyMDEContainer = easyMDE.element.parentNode.querySelector('.EasyMDEContainer');
    if (easyMDEContainer) {
        const observer = new MutationObserver(mutationsList => {
            for (const mutation of mutationsList) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const isSideBySide = easyMDEContainer.classList.contains('sided') || // EasyMDE v1.x.x
                                         easyMDEContainer.classList.contains('sided--no-fullscreen') || // EasyMDE v2.x.x
                                         easyMDEContainer.classList.contains('sided--fullscreen'); // EasyMDE v2.x.x
                    if (isSideBySide) {
                        editorAreaWrapper.classList.add('side-by-side-active');
                        // Asegurarse que el contenido del preview se actualiza al entrar en modo side-by-side
                        document.getElementById('preview').innerHTML = marked.parse(easyMDE.value());
                    } else {
                        editorAreaWrapper.classList.remove('side-by-side-active');
                    }
                }
            }
        });
        observer.observe(easyMDEContainer, { attributes: true });
    } else {
        console.error("No se pudo encontrar EasyMDEContainer para el MutationObserver.");
    }

    loadFileTree();
    previewEl.innerHTML = '<p style="color: var(--text-muted); text-align: center; margin-top: 50px;">Seleccione un archivo para editar.</p>';
});
