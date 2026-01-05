document.addEventListener("DOMContentLoaded", function () {

    const dataDiv = document.getElementById("dashboard-data");
    if (!dataDiv) {
        console.error("dashboard-data div not found");
        return;
    }
    const gradeData = [
        Number(dataDiv.dataset.aplus),
        Number(dataDiv.dataset.a),
        Number(dataDiv.dataset.b),
        Number(dataDiv.dataset.c)
    ];

    new Chart(document.getElementById('gradeChart'), {
        type: 'pie',
        data: {
            labels: ['A+', 'A', 'B', 'C'],
            datasets: [{
                data: gradeData
            }]
        }
    });
    const subjects = JSON.parse(dataDiv.dataset.subjects);

    new Chart(document.getElementById('subjectChart'), {
        type: 'bar',
        data: {
            labels: subjects.map(s => s.name),
            datasets: [{
                label: 'Students',
                data: subjects.map(s => Number(s.count))
            }]
        }
    });
    const subjectAvg = JSON.parse(dataDiv.dataset.subjectAvg);

    new Chart(document.getElementById('subjectAvgChart'), {
        type: 'line',
        data: {
            labels: subjectAvg.map(s => s.name),
            datasets: [{
                label: 'Average Marks',
                data: subjectAvg.map(s => s.avg),
                tension: 0.4
            }]
        }
    });
    new Chart(document.getElementById('passFailChart'), {
        type: 'doughnut',
        data: {
            labels: ['Pass', 'Fail'],
            datasets: [{
                data: [
                    Number(dataDiv.dataset.pass),
                    Number(dataDiv.dataset.fail)
                ]
            }]
        }
    });

});
