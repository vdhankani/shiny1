#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(bigrquery)

# Define UI for application that draws a histogram
ui <- shinyUI(fluidPage(
   
   # Application title
   titlePanel("Differential Gene Expression "),
   
   # Drop-down list of genes
   selectInput(inputId="gene",label="Select a gene:",choices=c("TP53",'PTEN','ADAM12'),selected="TP53"),
   
   #Drop-down list of clinical features
   selectInput(inputId = "clin",label="Select a clinical feature",choices=c("gender","histological_type","hpv_status","race"),selected = "Gender"),
   
   # Show a plot of the generated distribution
   plotOutput(outputId="distPlot")
     # )
   )
)

# Define server logic required to draw a histogram
server <- shinyServer(function(input, output) {
    
  output$distPlot <- renderPlot({
    querySql = paste("SELECT normalized_count,",input$clin, 
                      " FROM [isb-cgc:tcga_201607_beta.mRNA_UNC_HiSeq_RSEM] expr ", 
                      "JOIN [isb-cgc:tcga_201607_beta.Clinical_data] clin ",
                      "ON expr.ParticipantBarcode = clin.ParticipantBarcode ",
                      "WHERE HGNC_gene_symbol = '",input$gene,"'",sep="")   
    result = query_exec(querySql,project='isb-cgc')
    
    #plot(density(as.numeric(result$normalized_count)))
    boxplot(result$normalized_count~result[[2]],main=input$gene,xlab=input$clin)
   })
})

# Run the application 
shinyApp(ui = ui, server = server)

