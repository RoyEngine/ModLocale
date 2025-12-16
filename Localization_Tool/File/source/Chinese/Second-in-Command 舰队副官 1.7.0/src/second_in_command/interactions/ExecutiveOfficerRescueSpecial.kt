package second_in_command.interactions

import com.fs.starfarer.api.campaign.InteractionDialogAPI
import com.fs.starfarer.api.impl.campaign.rulecmd.salvage.SalvageSpecialInteraction
import com.fs.starfarer.api.impl.campaign.rulecmd.salvage.SalvageSpecialInteraction.SalvageSpecialData
import com.fs.starfarer.api.impl.campaign.rulecmd.salvage.special.BaseSalvageSpecial
import com.fs.starfarer.api.util.Misc
import second_in_command.SCUtils
import second_in_command.specs.SCOfficer

class ExecutiveOfficerRescueSpecial(var officer: SCOfficer) : SalvageSpecialData {

    override fun createSpecialPlugin(): SalvageSpecialInteraction.SalvageSpecialPlugin {
        return ExecutiveOfficerRescueSpecialInteraction(officer)
    }
}

class ExecutiveOfficerRescueSpecialInteraction(var officer: SCOfficer) : BaseSalvageSpecial() {

    val OPEN = "open"
    val NOT_NOW = "not_now"

    override fun init(dialog: InteractionDialogAPI?, specialData: Any?) {
        super.init(dialog, specialData)
        text.addPara("在进行初步评估时，你的搜救人员发现了一个仍在使用备用电源运行的低温休眠舱。")

        options.clearOptions()
        options.addOption("尝试打开休眠舱", OPEN)
        options.addOption("不是现在", NOT_NOW)
    }

    override fun optionSelected(optionText: String?, optionData: Any?) {

        if (optionData == OPEN) {

            var plugin = officer.getAptitudePlugin()

            text.addPara("解冻流程结束，休眠舱被打开了。 " +
                    "其中沉睡的是一名{执行军官}，出于对你提供救助的感激，决定加入你的舰队。", Misc.getTextColor(), Misc.getHighlightColor(), "执行军官")

            text.setFontSmallInsignia()
            text.addParagraph("${officer.person.nameString} (等级 ${officer.getCurrentLevel()}) 加入了你的舰队",  Misc.getPositiveHighlightColor())
            text.setFontInsignia()

            text.addPara("${officer.person.heOrShe.capitalize()} 进一步解释了${officer.person.hisOrHer}具备的技能，希望这能对你起到帮助。", Misc.getTextColor(), plugin.getColor(), "${plugin.getName()}")

         /*   var tooltip = text.beginTooltip()

            tooltip.addPara("Aptitude: ${plugin.getName()}", 0f, Misc.getTextColor(), plugin.getColor(), "${plugin.getName()}")

            tooltip.addSpacer(10f)

            tooltip.addPara("\"${plugin.getDescription()}\"", 0f)
            text.addTooltip()*/

            SCUtils.showSkillOverview(dialog, officer)

            dialog.textPanel.addPara("\"这是对我天赋的初步概述。一开始，只有第一项技能处于激活状态，不过" +
                    "顺利的话，随着我进一步融入你舰队的运作体系，我将最多能发挥其中 6 项技能的潜力。\"",
                Misc.getTextColor(), Misc.getHighlightColor(), "6")

            SCUtils.getPlayerData().addOfficerToFleet(officer)

            isDone = true
            setShowAgain(false)
        } else {
            isDone = true
            setEndWithContinue(false)
            setShowAgain(true)
        }

        //If Successful
       /* isDone = true
        setShowAgain(false)*/

        //If said "Not now"
        /*isDone = true
        setEndWithContinue(false)
        setShowAgain(true)*/
    }



}