package second_in_command.interactions.rules

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.InteractionDialogAPI
import com.fs.starfarer.api.campaign.InteractionDialogPlugin
import com.fs.starfarer.api.campaign.RuleBasedDialog
import com.fs.starfarer.api.campaign.rules.MemKeys
import com.fs.starfarer.api.campaign.rules.MemoryAPI
import com.fs.starfarer.api.characters.PersonAPI
import com.fs.starfarer.api.combat.EngagementResultAPI
import com.fs.starfarer.api.impl.campaign.rulecmd.AddRemoveCommodity
import com.fs.starfarer.api.impl.campaign.rulecmd.BaseCommandPlugin
import com.fs.starfarer.api.impl.campaign.rulecmd.FireAll
import com.fs.starfarer.api.ui.CustomPanelAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import lunalib.lunaExtensions.addLunaElement
import org.lwjgl.input.Keyboard
import second_in_command.SCUtils
import second_in_command.specs.SCBaseSkillPlugin
import second_in_command.specs.SCOfficer
import second_in_command.specs.SCSpecStore
import second_in_command.ui.elements.*
import second_in_command.ui.tooltips.SCSkillTooltipCreator


class SCOfficerHireDialog : BaseCommandPlugin() {
    override fun execute(ruleId: String?, dialog: InteractionDialogAPI, params: MutableList<Misc.Token>?, memoryMap: MutableMap<String, MemoryAPI>?): Boolean {
        dialog.optionPanel.clearOptions()

        var plugin = SCOfficerHireDialogDelegate(dialog.plugin, dialog.interactionTarget.activePerson)
        dialog.plugin = plugin
        plugin.init(dialog)

        return true
    }
}

class SCOfficerHireDialogDelegate(var original: InteractionDialogPlugin, var person: PersonAPI) : InteractionDialogPlugin {

    lateinit var dialog: InteractionDialogAPI



    override fun init(dialog: InteractionDialogAPI) {

        this.dialog = dialog

        dialog.optionPanel.clearOptions()

        dialog.optionPanel.addOption("\"这视情况而定。你能做些什么？\"", "sc_convo_question")

        dialog.optionPanel.addOption("结束对话", "sc_convo_end")
        dialog.optionPanel.setShortcut("sc_convo_end", Keyboard.KEY_ESCAPE, false, false, false, true)
    }

    fun returnToPrevious() {
        dialog.optionPanel.clearOptions()
        dialog.textPanel.addPara("结束对话", Misc.getBasePlayerColor(), Misc.getBasePlayerColor())
        dialog.textPanel.addPara("你切断了通信链接。")

        dialog.plugin = original
        dialog.visualPanel.hideFirstPerson()
        dialog.interactionTarget.activePerson = null
        (dialog.plugin as RuleBasedDialog).notifyActivePersonChanged()

        FireAll.fire(null, dialog, memoryMap, "PopulateOptions")
    }

    override fun optionSelected(optionText: String?, optionData: Any?) {

        var aptitudeId = person.memoryWithoutUpdate.getString("\$sc_officer_aptitude")
        var aptitudePlugin = SCSpecStore.getAptitudeSpec(aptitudeId)!!.getPlugin()

        var credits = Global.getSector().playerFleet.cargo.credits
        var cost = 10000f

        if (optionData == "sc_convo_question") {
            dialog.textPanel.addPara("\"这视情况而定。你能做些什么？\"", Misc.getBasePlayerColor(), Misc.getBasePlayerColor())

            dialog.optionPanel.clearOptions()

            dialog.textPanel.addPara("你向 ${person.nameString} 提出一些问题，以确定${person.hisOrHer}的具体能力水平。")

            var scOfficer = SCOfficer(person, aptitudeId)


            SCUtils.showSkillOverview(dialog, scOfficer)

            dialog.textPanel.addPara("\"这是对我天赋的初步概述。一开始，只有第一项技能处于激活状态，不过" +
                    "顺利的话，随着我进一步融入你舰队的运作体系，我将最多能发挥其中 6 项技能的潜力。",
                Misc.getTextColor(), Misc.getHighlightColor(), "6")

            var costString = Misc.getDGSCredits(cost)
            var creditsString = Misc.getDGSCredits(credits.get())

            dialog.textPanel.addPara("我希望你能一次性支付 $costString 星币作为签约费用，至于未来的薪资可以以后再做讨论。" +
                    "一旦转账完成，一个小时内我就能做好登舰准备。\"", Misc.getTextColor(), Misc.getHighlightColor(), "$costString")

            dialog.textPanel.addPara("你现有 $creditsString 星币可用。", Misc.getTextColor(), Misc.getHighlightColor(), "$creditsString")

            dialog.optionPanel.addOption("雇佣 ${person.himOrHer}", "sc_convo_hire")

            if (credits.get() <= cost) {
                dialog.optionPanel.setEnabled("sc_convo_hire", false)
                dialog.optionPanel.setTooltip("sc_convo_hire", "你的星币不足。")
            }

            dialog.optionPanel.addOption("结束对话", "sc_convo_end")
            dialog.optionPanel.setShortcut("sc_convo_end", Keyboard.KEY_ESCAPE, false, false, false, true)
        }

        if (optionData == "sc_convo_hire") {
            dialog.textPanel.addPara("雇佣 ${person.himOrHer}", Misc.getBasePlayerColor(), Misc.getBasePlayerColor())

            var scOfficer = SCOfficer(person, aptitudeId)

            credits.subtract(cost)
            AddRemoveCommodity.addCreditsLossText(cost.toInt(), dialog.textPanel)
            dialog.textPanel.addParagraph("${person.nameString} (等级 ${scOfficer.getCurrentLevel()}) 加入了你的舰队",  Misc.getPositiveHighlightColor())

            SCUtils.getPlayerData().addOfficerToFleet(scOfficer)

            dialog.interactionTarget.market.commDirectory.removePerson(person)

            returnToPrevious()
        }

        if (optionData == "sc_convo_end") {
            returnToPrevious()
        }
    }

    override fun optionMousedOver(optionText: String?, optionData: Any?) {

    }

    override fun advance(amount: Float) {

    }

    override fun backFromEngagement(battleResult: EngagementResultAPI?) {

    }

    override fun getContext(): Any? {
        return null
    }

    override fun getMemoryMap(): MutableMap<String, MemoryAPI> {
        return original.memoryMap
    }

}