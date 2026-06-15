// ======================================
// FILE INPUT PREVIEW
// ======================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const fileInput =
            document.querySelector(
                'input[type="file"]'
            );

        if (!fileInput) {
            return;
        }

        createPreviewArea();

        fileInput.addEventListener(
            "change",
            handleFileSelect
        );
    }
);

// ======================================
// RENAME MODAL
// ======================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const renameModal =
            document.getElementById(
                "renameModal"
            );

        if (!renameModal) {
            return;
        }

        renameModal.addEventListener(
            "show.bs.modal",
            function (event) {

                const button =
                    event.relatedTarget;

                document.getElementById(
                    "renameMediaId"
                ).value =
                    button.dataset.id;

                document.getElementById(
                    "renameMediaName"
                ).value =
                    button.dataset.name;
            }
        );
    }
);


// ======================================
// QR CODE MODAL
// ======================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const qrModal =
            document.getElementById(
                "qrModal"
            );

        if (!qrModal) {
            return;
        }

        qrModal.addEventListener(
            "show.bs.modal",
            function (event) {

                const button =
                    event.relatedTarget;

                document.getElementById(
                    "qrModalImage"
                ).src =
                    button.dataset.qr;

                document.getElementById(
                    "qrModalTitle"
                ).innerText =
                    button.dataset.name;
            }
        );
    }
);


// ======================================
// DRAG & DROP
// ======================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const dropZone =
            document.getElementById(
                "dropZone"
            );

        const input =
            document.getElementById(
                "mediaInput"
            );

        if (
            !dropZone ||
            !input
        ) {
            return;
        }

        dropZone.addEventListener(
            "click",
            function () {

                input.click();

            }
        );

        dropZone.addEventListener(
            "dragover",
            function (e) {

                e.preventDefault();

                dropZone.classList.add(
                    "dragover"
                );
            }
        );

        dropZone.addEventListener(
            "dragleave",
            function () {

                dropZone.classList.remove(
                    "dragover"
                );
            }
        );

        dropZone.addEventListener(
            "drop",
            function (e) {

                e.preventDefault();

                dropZone.classList.remove(
                    "dragover"
                );

                input.files =
                    e.dataTransfer.files;

                input.dispatchEvent(
                    new Event("change")
                );
            }
        );
    }
);

// ======================================
// COPY LINK BUTTON
// ======================================

document.addEventListener(
    "click",
    function (event) {

        if (
            event.target.classList.contains(
                "copy-link-btn"
            )
        ) {

            const url =
                event.target.dataset.url;

            navigator.clipboard.writeText(
                url
            );

            event.target.innerText =
                "Copied!";

            setTimeout(
                function () {

                    event.target.innerText =
                        "Copy Link";

                },
                2000
            );
        }
    }
);


// ======================================
// PREVIEW AREA
// ======================================

function createPreviewArea() {

    const fileInput =
        document.querySelector(
            'input[type="file"]'
        );

    const preview =
        document.createElement("div");

    preview.id =
        "uploadPreview";

    preview.className =
        "upload-preview text-center";

    preview.innerHTML =
        `
        <h5 class="mb-3">
            Preview
        </h5>

        <img
            id="previewImage"
            src=""
            alt="Preview">

        <div
            id="previewInfo"
            class="mt-3">
        </div>
        `;

    fileInput.parentNode.appendChild(
        preview
    );
}


// ======================================
// HANDLE FILE SELECT
// ======================================

function handleFileSelect(event) {

    const file =
        event.target.files[0];

    if (!file) {
        return;
    }

    const mediaName =
        document.getElementById(
            "mediaName"
        );

    if (mediaName) {

        const filename =
            file.name.replace(
                /\.[^/.]+$/,
                ""
            );

        mediaName.value =
            filename;
    }

    validateFileSize(file);

    showPreview(file);
}


// ======================================
// VALIDASI UKURAN
// ======================================

function validateFileSize(file) {

    const maxImageSize =
        10 * 1024 * 1024;

    const maxVideoSize =
        100 * 1024 * 1024;

    if (
        file.type.startsWith("image/")
    ) {

        if (
            file.size >
            maxImageSize
        ) {

            alert(
                "Ukuran gambar maksimal 10 MB"
            );

            location.reload();
        }
    }

    if (
        file.type.startsWith("video/")
    ) {

        if (
            file.size >
            maxVideoSize
        ) {

            alert(
                "Ukuran video maksimal 100 MB"
            );

            location.reload();
        }
    }
}


// ======================================
// PREVIEW FILE
// ======================================

function showPreview(file) {

    const preview =
        document.getElementById(
            "uploadPreview"
        );

    const image =
        document.getElementById(
            "previewImage"
        );

    const info =
        document.getElementById(
            "previewInfo"
        );

    preview.style.display =
        "block";

    if (
        file.type.startsWith(
            "image/"
        )
    ) {

        const reader =
            new FileReader();

        reader.onload =
            function (e) {

                image.src =
                    e.target.result;

                image.style.display =
                    "inline-block";
            };

        reader.readAsDataURL(file);
    }
    else {

        image.style.display =
            "none";
    }

    const sizeMB =
        (
            file.size /
            1024 /
            1024
        ).toFixed(2);

    info.innerHTML =
        `
        <div class="card mt-3">
            <div class="card-body">

                <strong>
                    ${file.name}
                </strong>

                <br>

                Ukuran:
                ${sizeMB} MB

                <br>

                Tipe:
                ${file.type}

            </div>
        </div>
        `;
}


// ======================================
// LOADING INDICATOR
// ======================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        createLoadingOverlay();

        const uploadForm =
            document.getElementById(
                "uploadForm"
            );

        if (
            uploadForm
        ) {

            uploadForm.addEventListener(
                "submit",
                function () {

                    showLoading();
                }
            );
        }
    }
);


// ======================================
// CREATE OVERLAY
// ======================================

function createLoadingOverlay() {

    const overlay =
        document.createElement("div");

    overlay.id =
        "loadingOverlay";

    overlay.className =
        "loading-overlay";

    overlay.innerHTML =
        `
        <div
            class="loading-spinner">
        </div>

        <div
            class="loading-text">

            Mengupload media dan membuat QR Code...

        </div>
        `;

    document.body.appendChild(
        overlay
    );
}


// ======================================
// SHOW LOADING
// ======================================

function showLoading() {

    const overlay =
        document.getElementById(
            "loadingOverlay"
        );

    if (overlay) {

        overlay.style.display =
            "flex";
    }
}


// ======================================
// HIDE LOADING
// ======================================

function hideLoading() {

    const overlay =
        document.getElementById(
            "loadingOverlay"
        );

    if (overlay) {

        overlay.style.display =
            "none";
    }
}


// ======================================
// AUTO HIDE ALERT
// ======================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const alerts =
            document.querySelectorAll(
                ".alert"
            );

        alerts.forEach(
            function (alert) {

                setTimeout(
                    function () {

                        alert.remove();

                    },
                    5000
                );
            }
        );
    }
);