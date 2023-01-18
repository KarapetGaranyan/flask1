document.addEventListener('DOMContentLoaded', () => {
    if(document.querySelector('.error')) {
        setTimeout(() => {
            document.querySelector('.error').style.top = '-100px';
        }, 4000);
    }

    const form = document.querySelector('.form');
    const fileUpload = document.querySelector('#upload-file');
    fileUpload.addEventListener('change', (e) => {
        const filename = e.target.value.slice(e.target.value.search('path')+5);
        document.querySelector('.choosen-filename').innerHTML = filename;
        document.querySelector('.choosen-filename').style.top = '0px';
        setTimeout(() => form.submit(), 1200);
    })

    const RKO = document.querySelector('.form__btn');
    const RKOModalClose = document.querySelector('.modal-exit-btn');
    RKOModalClose.addEventListener('click', () => {
        document.querySelector('.rko-modal').style.display = 'none';
    })
    RKO.addEventListener('click', (e) => {
        e.preventDefault()
        document.querySelector('.rko-modal').style.display = 'flex';
    })
});
