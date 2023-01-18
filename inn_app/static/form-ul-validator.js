document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector('form');
    const sumbitBtn = document.querySelector("button[type='submit']")
    sumbitBtn.addEventListener("click", function (event) {
        event.preventDefault()
        console.log('submt')
        if(telValidator()) return
        else if(emailValidator()) return
        else if(domenValidator()) return
        else if(bankValidator()) return
        else if(okpoValidator()) return
        form.submit()
    });


    function telValidator() {
        const telephone = document.querySelector("input[name='telephone']").value;
        const telRegex = /^\d{10}$/;
        if (!telephone.match(telRegex)) {
            setError("Телефон введен неврено!")
            return true
        }
        return false
    }

    function emailValidator() {
        const email = document.querySelector("input[name='email']").value
        const emailRegex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
        if (!email.match(emailRegex)) {
            setError("Эл.почта введена неврено!")
            return true
        }
        return false
    }

    function domenValidator() {
        const domen = document.querySelector("input[name='domen']").value
        const domenRegex = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
        if(!domen.match(domenRegex)) {
            setError("Адрес сайта введен неверно!")
            return true
        }
        return false
    }

    function bankValidator() {
        const bank = document.querySelector("input[name='bank']").value;
        const bankRegex = /^40702\d{15}$/;
        const bankRegex2 = /^40802\d{15}$/;
        if(!bank.match(bankRegex)) {
            if (!bank.match(bankRegex2)) {
                setError("Счет введен неверно!")
                return true
            }
        }
        return false
    }

    function okpoValidator() {
        if(!document.querySelector("input[name='okpo']")) {
            return false
        };
        const okpo = document.querySelector("input[name='okpo']").value;
        const okpoRegex = /^\d{8}$/;
        if(!okpo.match(okpoRegex)) {
            setError("ОКПО введен неверно!")
            return true
        }
        return false
    }

    function setError(text) {
        document.querySelector('.error').innerHTML = text
        document.querySelector('.error').style.top = '0px';
        setTimeout(() => {
            document.querySelector('.error').style.top = '-100px'
        }, 4000)
    }
});

