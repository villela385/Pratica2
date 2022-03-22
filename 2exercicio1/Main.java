import java.util.Scanner;
class Main {
  public static void main(String[] args) {
    Scanner ler = new Scanner(System.in);
    int opt;
    Double totalGasto, parcelas, numParcelas;
    do{
      System.out.println("Digite o total gasto pelo cliente: R$");
      totalGasto = ler.nextDouble();
      System.out.println(totalGasto);
      if (totalGasto != -1.0){ 
        System.out.println("1 - À vista (10% de desconto)");
        System.out.println("2 - Parcelado em 2x");
        System.out.println("3 - Parcelado de 3x a 6x (3% de juros ao mês)");
        opt = ler.nextInt();
        switch(opt){
          case 1:
            System.out.printf("Valor: R$%.2f\n", totalGasto - (totalGasto * 0.10));
            break;
          case 2:
            System.out.printf("Duas parcelas de: R$%.2f\n", totalGasto / 2.0);
            break;
          case 3:
            System.out.println("Quantas parcelas? (entre 3 e 6)");
            parcelas = ler.nextDouble();
            if (parcelas >= 3 && parcelas <= 6){
              if(totalGasto < 500){
                System.out.println("Escolha nova forma de pagamento");
              } else {  
                numParcelas= parcelas * 0.03;
                System.out.println(parcelas + " parcelas de: R$" + (totalGasto / parcelas) * 1.03);
              }
            } else {
              System.out.println("ERRO FATAL! Digite um valor entre 3 e 6");
              totalGasto = -1.0;
            }
            break;
        }
      }
    } while(totalGasto != -1.0);
  }
}