import java.util.Scanner;

public class Main {
  public static void main(String[] args) {
    Scanner ler = new Scanner(System.in);
    int NumeroVoo, NumPoltrona, num = 0;
    String CPF, nome;
    do{
      System.out.println("1 - Cadastrar Passageiro");
      System.out.println("2 - Check in");
      System.out.println("3 - Cancelar Voo");
      System.out.println("4 - Sair");
      num = ler.nextInt();
      switch (num){
        case 1:
          System.out.println ("Digite seu nome");
          nome = ler.next();
          System.out.println ("Digite seu CPF");
          CPF = ler.next();
          System.out.println ("Digite seu número de voo");
          NumeroVoo = ler.nextInt();
          
          System.out.println ("Cadastro efetuado com sucesso.");

          break;
        case 2:
          System.out.println ("Digite seu CPF");
          CPF = ler.nextLine();
          System.out.println ("Digite o número do voo");
          NumeroVoo = ler.nextInt();
          System.out.println ("Digite o número da poltrona");
          NumPoltrona = ler.nextInt();

          
          System.out.println ("Check in efetuado com sucesso");
          break;
      }
    } 
  }
}