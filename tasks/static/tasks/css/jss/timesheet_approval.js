const reports = JSON.parse(
    document.getElementById("timesheet-data").textContent
);


const tableBody = document.querySelector('#reportTable tbody');
const reportCount = document.querySelector('#reportCount');
const reportTitle = document.querySelector('#reportTitle');
const reportMeta = document.querySelector('#reportMeta');
const reportOptions = document.querySelector('#reportOptions');
const dateFilterInput = document.querySelector('#sortDatePicker');
const resetBtn = document.querySelector('#resetBtn');
const toast = document.querySelector('#toast');

const reportTasks = document.querySelector('#reportTasks');
const reportHours = document.querySelector('#reportHours');
const reportStatus = document.querySelector('#reportStatus');


let selectedIndex = 0;

let allReports = [...reports];

let currentReports = [...allReports];



/*
    Format date
*/
function formatDate(value) {

    const date = new Date(value);

    return date.toLocaleDateString('en-US', {

        month:'short',
        day:'numeric',
        year:'numeric'

    });

}




/*
    Display timesheet rows
*/
function renderReportRows(){

    tableBody.innerHTML = "";


    currentReports.forEach((report,index)=>{


        const row=document.createElement("tr");


        row.dataset.index=index;


        row.innerHTML=`

            <td>
                <button 
                    type="button"
                    class="employee-link">
                    ${report.employee}
                </button>
            </td>


            <td>
                ${formatDate(report.date)}
            </td>


            <td>
                ${report.hours} hrs
            </td>


            <td>
                ${report.status}
            </td>

        `;



        row.querySelector(".employee-link")
        .addEventListener("click",(event)=>{

            event.stopPropagation();

            selectReport(index);

        });



        row.addEventListener(
            "click",
            ()=>{
                selectReport(index);
            }
        );



        row.tabIndex=0;



        row.addEventListener(
            "keydown",
            (event)=>{

                if(event.key==="Enter" || event.key===" "){

                    event.preventDefault();

                    selectReport(index);

                }

            }
        );



        if(index===selectedIndex){

            row.classList.add("selected");

        }



        tableBody.appendChild(row);



    });



    reportCount.textContent =
        `${currentReports.length} total`;

}





/*
    Select employee timesheet
*/
function selectReport(index){


    selectedIndex=index;


    const report=currentReports[index];


    const rows=
    Array.from(
        tableBody.querySelectorAll("tr")
    );


    rows.forEach(row=>{

        row.classList.toggle(
            "selected",
            Number(row.dataset.index)===index
        );

    });



    reportTitle.textContent =
        `${report.employee}'s Timesheet`;



    reportMeta.innerHTML=`

        <span>
            Date: ${formatDate(report.date)}
        </span>

        <span>
            Hours: ${report.hours}
        </span>

    `;



    reportTasks.textContent =
        report.tasks || 
        "No task description";



    if(reportHours){

        reportHours.textContent =
            report.hours+" hours";

    }



    if(reportStatus){

        reportStatus.textContent =
            report.status;

    }



    renderReportOptions(report);

}





/*
    Manager actions
*/
function renderReportOptions(report){


    reportOptions.innerHTML="";



    const options=[

        "Approve",
        "Reject",
        "Add Comment",
        "View Full Report"

    ];



    options.forEach(option=>{


        const button=
        document.createElement("button");



        button.type="button";

        button.className="option-btn";

        button.textContent=option;



        button.addEventListener(
            "click",
            ()=>{

                managerAction(
                    option,
                    report.id
                );

            }
        );



        reportOptions.appendChild(button);


    });


}





/*
    Approve Reject API call
*/
function managerAction(action,id){



    if(action==="Approve"){


        fetch(
            `/timesheets/approve/${id}/`,
            {

                method:"POST",

                headers:{

                    "X-CSRFToken":getCookie("csrftoken")

                }

            }

        )
        .then(()=>{

            showToast(
                "Timesheet Approved"
            );


            setTimeout(
                ()=>{
                    location.reload();
                },
                1000
            );


        });


    }




    else if(action==="Reject"){


        fetch(
            `/timesheets/reject/${id}/`,
            {

                method:"POST",

                headers:{

                    "X-CSRFToken":
                    getCookie("csrftoken")

                }

            }

        )
        .then(()=>{


            showToast(
                "Timesheet Rejected"
            );


            setTimeout(
                ()=>{
                    location.reload();
                },
                1000
            );


        });


    }



    else{


        showToast(
            `Manager action : ${action}`
        );


    }



}





/*
    Toast message
*/
function showToast(message){


    toast.textContent=message;


    toast.classList.add("show");


    clearTimeout(
        window.toastTimer
    );



    window.toastTimer=setTimeout(()=>{


        toast.classList.remove("show");


    },2800);



}





/*
    Filter by date
*/
function filterReportsByDate(){


    const selectedDate =
        dateFilterInput.value;



    if(!selectedDate){


        currentReports=[
            ...allReports
        ];


    }


    else{


        currentReports =
        allReports.filter(
            report=>
            report.date===selectedDate
        );


    }



    selectedIndex=0;


    renderReportRows();



    if(currentReports.length){

        selectReport(0);

    }

    else{


        clearReportDetails();

    }


}





/*
    Reset
*/
function resetOrder(){


    dateFilterInput.value="";


    currentReports=[
        ...allReports
    ];


    selectedIndex=0;


    renderReportRows();



    if(currentReports.length){

        selectReport(0);

    }



}





function clearReportDetails(){


    reportTitle.textContent=
        "No report selected";


    reportMeta.innerHTML=
        "<span>Date : -</span>";



    reportTasks.textContent=
        "No employee reports available";



    reportOptions.innerHTML=
    `
    <span class="option-help">
        Select report to view options
    </span>
    `;


}





/*
    CSRF Token
*/
function getCookie(name){


    let cookieValue=null;


    if(document.cookie){

        const cookies =
        document.cookie.split(";");


        cookies.forEach(cookie=>{


            cookie=cookie.trim();



            if(cookie.startsWith(name+"=")){


                cookieValue=
                decodeURIComponent(
                    cookie.substring(
                        name.length+1
                    )
                );

            }


        });

    }


    return cookieValue;


}





dateFilterInput.addEventListener(
    "change",
    filterReportsByDate
);



resetBtn.addEventListener(
    "click",
    resetOrder
);



renderReportRows();



if(currentReports.length){

    selectReport(0);

}
else{

    clearReportDetails();

}