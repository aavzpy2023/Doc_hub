// --- /app/static/editor_logic.js ---
document.addEventListener('DOMContentLoaded', () => {
    // ==========================================================================
    // 1. Inicialización y Autenticación
    // ==========================================================================
    const token = localStorage.getItem('docuhub_token');
    if (!token) { window.location.href = '/login'; }
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
    const publishBtn = document.getElementById('publish-btn'); // Asumimos que este botón sigue existiendo y tiene su propia lógica
    const statusEl = document.getElementById('status-message');
    const editorAreaWrapper = document.getElementById('editor-area-wrapper');

    let currentFilePath = null; // Esta será la ruta relativa al directorio DOCS_SOURCE_DIR
    let easyMDE;

    function renderTree(nodes, container) {
        const ul = document.createElement('ul');
        nodes.forEach(node => {
            const li = document.createElement('li');
            if (node.type === 'directory') {
                // Añadir un data-path a los directorios podría ser útil para expansiones futuras,
                // pero para la funcionalidad actual no es estrictamente necesario.
                li.innerHTML = `<span class="directory" data-path="${node.path}">📁 ${node.name.replace(/_/g, ' ')}</span>`;
                if (node.children && node.children.length > 0) {
                    renderTree(node.children, li); // Pasar los hijos para la recursión
                }
            } else if (node.type === 'file' && node.name.toLowerCase().endsWith('.md')) {
                li.innerHTML = `<span class="file" data-path="${node.path}">📄 ${node.name}</span>`;
            }

            // Solo añadir el LI si tiene contenido (evita LIs vacíos si un directorio no tiene .md o no es un .md)
            if (li.innerHTML) {
                ul.appendChild(li);
            }
        });
        // Solo añadir el UL si tiene LIs (evita ULs vacíos)
        if (ul.hasChildNodes()) {
            container.appendChild(ul);
        }
    }

    async function loadFileTree() {
        fileTreeEl.innerHTML = '<p style="color: var(--text-muted); padding: 1rem;">Cargando estructura de /docs...</p>';
        try {
            const response = await fetch('/api/v1/project-docs/tree', { headers: authHeaders });
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return; // Evitar más procesamiento si se redirige
                }
                const errorData = await response.json().catch(() => ({ detail: "Error desconocido al obtener el árbol de archivos." }));
                throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail || "No se pudo obtener el árbol de archivos."}`);
            }
            const treeData = await response.json();
            fileTreeEl.innerHTML = '';
            if (treeData.length === 0) {
                fileTreeEl.innerHTML = '<p style="color: var(--text-muted); padding: 1rem;">No se encontraron documentos Markdown en la carpeta /docs.</p>';
            } else {
                renderTree(treeData, fileTreeEl);
            }
        } catch (error) {
            console.error("Error loading project file tree:", error);
            fileTreeEl.innerHTML = `<p style="color: red; padding: 1rem;">Error al cargar árbol de archivos: ${error.message}</p>`;
        }
    }

    async function loadFileContent(path) {
        currentFilePath = path;
        if (previewEl && previewEl.style.display !== 'none' && !editorAreaWrapper.classList.contains('side-by-side-active')) {
            previewEl.innerHTML = '<p style="color: var(--text-muted); text-align: center; margin-top: 50px;">Cargando contenido...</p>';
        }
        saveBtn.disabled = true;
        if (easyMDE) easyMDE.value("Cargando..."); // Mensaje en el editor mientras carga

        try {
            const response = await fetch(`/api/v1/project-docs/content/${path}`, { headers: authHeaders });
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                const errorData = await response.json().catch(() => ({ detail: "Error desconocido al cargar el contenido." }));
                throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail || "No se pudo cargar el contenido."}`);
            }
            const data = await response.json();
            if (easyMDE) {
                easyMDE.value(data.content);
                easyMDE.codemirror.clearHistory(); // Limpiar historial de undo para el nuevo archivo
                easyMDE.codemirror.focus(); // Poner el foco en el editor
                if (editorAreaWrapper.classList.contains('side-by-side-active') && previewEl) {
                     previewEl.innerHTML = marked.parse(data.content);
                }
            }
            saveBtn.disabled = false;
            statusEl.textContent = `Archivo '${path}' cargado.`;
            setTimeout(() => statusEl.textContent = '', 3000);

        } catch (error) {
            console.error(`Error loading project file content for path "${path}":`, error);
            if (easyMDE) easyMDE.value(`## Error al cargar ${path}\n\n${error.message}`);
            statusEl.textContent = `Error al cargar: ${error.message}`;
            // No deshabilitar saveBtn aquí, ya que podría haber contenido de error que el usuario quiera editar/guardar
        }
    }

    saveBtn.addEventListener('click', async () => {
        if (!currentFilePath || !easyMDE) {
            statusEl.textContent = 'Ningún archivo activo para guardar.';
            setTimeout(() => statusEl.textContent = '', 3000);
            return;
        }
        statusEl.textContent = 'Guardando...';
        saveBtn.disabled = true;
        try {
            const response = await fetch(`/api/v1/project-docs/content/${currentFilePath}`, {
                method: 'POST',
                headers: { ...authHeaders, 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: easyMDE.value() })
            });
            if (!response.ok) {
                 if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                 }
                 const errorData = await response.json().catch(() => ({ detail: "Error desconocido al guardar." }));
                 throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail || "No se pudo guardar el archivo."}`);
            }
            const result = await response.json();
            statusEl.textContent = result.message || '¡Archivo guardado exitosamente!';
        } catch (error) {
            console.error("Error saving project file:", error);
            statusEl.textContent = `Error al guardar: ${error.message}`;
        } finally {
            saveBtn.disabled = false;
            setTimeout(() => statusEl.textContent = '', 4000);
        }
    });

    // La lógica de publishBtn sigue siendo la misma si es para otro propósito.
    // Si 'publish' ahora significa algo relacionado con estos archivos de /docs,
    // necesitaría su propia lógica y endpoint.
    publishBtn.addEventListener('click', async () => {
        statusEl.textContent = 'Publicando sitio (lógica anterior)...'; // Placeholder
        // ... (lógica de publishBtn original si es diferente) ...
        // Ejemplo de placeholder para la lógica de MkDocs si este botón lo hiciera:
        // const response = await fetch('/api/v1/documents/publish', { method: 'POST', headers: authHeaders });
        // statusEl.textContent = response.ok ? '¡Sitio publicado!' : 'Error al publicar.';
        setTimeout(() => statusEl.textContent = '', 3000);
    });

    fileTreeEl.addEventListener('click', (e) => {
        const targetFile = e.target.closest('.file'); // Manejar clic en el span o su hijo
        if (targetFile && targetFile.dataset.path) {
            document.querySelectorAll('.file.active').forEach(el => el.classList.remove('active'));
            targetFile.classList.add('active');
            loadFileContent(targetFile.dataset.path);
        }
    });

    easyMDE = new EasyMDE({
        element: document.getElementById('markdown-editor'),
        spellChecker: false,
        status: ["lines", "words", "cursor"],
        toolbarTips: true,
        indentWithTabs: false,
        tabSize: 4,
        lineWrapping: true,
        toolbar: [
            "bold", "italic", "heading", "|",
            "quote", "unordered-list", "ordered-list", "|",
            "link", "image", "|",
            "side-by-side", "fullscreen", "|",
            "guide"
        ],
        previewRender: function(plainText, easyMDEInternalPreviewPanel) {
            const renderedHTML = marked.parse(plainText);
            if (previewEl) {
                previewEl.innerHTML = renderedHTML;
            }
            if (easyMDEInternalPreviewPanel) {
                easyMDEInternalPreviewPanel.className = 'editor-preview-side markdown-body';
                easyMDEInternalPreviewPanel.innerHTML = renderedHTML;
            }
            return renderedHTML;
        },
    });

    easyMDE.codemirror.on("change", () => {
        if (currentFilePath) { // Solo habilitar guardado si hay un archivo cargado
            saveBtn.disabled = false;
        } else {
            saveBtn.disabled = true;
        }
    });

    const easyMDEContainer = easyMDE.element.parentNode.querySelector('.EasyMDEContainer');
    if (easyMDEContainer) {
        const observer = new MutationObserver(mutationsList => {
            for (const mutation of mutationsList) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const isSideBySide = easyMDEContainer.classList.contains('sided') ||
                                         easyMDEContainer.classList.contains('sided--no-fullscreen') ||
                                         easyMDEContainer.classList.contains('sided--fullscreen');
                    if (isSideBySide) {
                        editorAreaWrapper.classList.add('side-by-side-active');
                        if (previewEl && easyMDE) {
                            previewEl.innerHTML = marked.parse(easyMDE.value());
                        }
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

    // Carga inicial del árbol de archivos del proyecto
    loadFileTree();

    if (previewEl) {
         previewEl.innerHTML = '<p style="color: var(--text-muted); text-align: center; margin-top: 50px;">Seleccione un archivo de /docs para editar o use F9 para alternar la vista previa.</p>';
    }
    if (!currentFilePath) { // Deshabilitar guardado si no hay archivo al inicio
        saveBtn.disabled = true;
    }
});
