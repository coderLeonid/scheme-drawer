void inputmatr(matrix a, int str, int sto)
{
    cout << " Введите построчно через пробел элементы" << endl;
    cout << " двумерного массива размера " << str << "x" << sto << endl;
    cout << " После ввода строки нажимайте <Enter>" << endl;
    for (int i = 0; i < str; i++)
        for (int j = 0; j < sto; j++)
            *(*(a + i) + j) = (str * sto - 1) - (sto * i + j); // на этапе тестирования происходит
    // автоматическое заполнение значений
    // элементов массива
}
