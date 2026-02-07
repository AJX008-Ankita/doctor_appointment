function searchDoctors() {
    const problem = document.getElementById("problem").value;

    fetch(`/api/search-doctors/?problem=${problem}`)
        .then(res => res.json())
        .then(data => {
            let html = "";

            if (data.length === 0) {
                html = `<div class="col-12 text-center text-muted">
                            No doctors found
                        </div>`;
            }

            data.forEach(doc => {
                html += `
                    <div class="col-md-4">
                        <div class="card mb-4 doctor-card">
                            <div class="card-body">
                                <h5>${doc.name}</h5>
                                <p>
                                    <strong>Specialization:</strong> ${doc.specialization}<br>
                                    <strong>Email:</strong> ${doc.email}
                                </p>
                                <button class="btn btn-success w-100">
                                    Select Doctor
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });

            document.getElementById("doctor-list").innerHTML = html;
        });
}
