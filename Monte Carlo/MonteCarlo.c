#include <stdio.h>
#include <Math.h>


double simpleMonteCarlo()
{
  double xmin= 0.0
  double xmax = M_PI;
  unsigned int nSamples = 10000, k;

  printf("Enter no. of sample: ")
  scanf("%ld",&k);
  if(k > 100)
    nSamples = k;

  double sum = 0.0
  for(unsigned int i = 1; x <= nSamples; i++){
     double x = randomNumber(xmin, xmax);
     double y1 = sin(x);
     double y = y1 * y1;
     sum += y;
  }/*END : for(i) */

  double yAvg = sum / (double)(nSamples);

  return yAvg * (xmax - xmin);
}

int main()
{
    double ans = simpleMonteCarlo();
    printf("Ans = %d",ans);

}